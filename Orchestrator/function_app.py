import azure.functions as func
import logging
from langchain import OpenAI
from langchain.chat_models import AzureChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from langchain.agents import AgentType, create_sql_agent
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
import pyodbc


os.environ["OPENAI_API_TYPE"]="azure"
os.environ["OPENAI_API_VERSION"]="2023-09-01-preview"
os.environ["OPENAI_API_BASE"]=""
os.environ["OPENAI_API_KEY"]=""
os.environ["OPENAI_CHAT_MODEL"]=""

os.environ["SQL_SERVER"]=""
os.environ["SQL_DB"]=""
os.environ["SQL_USERNAME"]="" 
os.environ["SQL_PWD"]=""

#creamos el motor SQL con sqlalchemy
#como es una base de datos Microsoft SQL Server utiliza el adaptador de conexión ODBC y por eso hay que importar pyodbc
def CreateSqlEngine():
    connection_url = URL.create(
        "mssql+pyodbc",
        username=os.getenv("SQL_USERNAME"),
        password=os.getenv("SQL_PWD"),
        host=os.getenv("SQL_SERVER"),
        port=1433,
        database=os.getenv("SQL_DB"),
        query={
            "driver": "ODBC Driver 17 for SQL Server",
            "TrustServerCertificate": "yes",
        },
    )

    return create_engine(connection_url)

#Iniciamos el LLM con Azure OpenAI
def InitializeAzureOpenAI():
    llm = AzureChatOpenAI(model=os.getenv("OPENAI_CHAT_MODEL"),
                      deployment_name=os.getenv("OPENAI_CHAT_MODEL"),
                      temperature=0, max_tokens=4000)
    
    return llm

#definimos el prompt con el rol System en donde se indican las instrucciones que puede ejecutar y el contexto por el cuál se moverá GPT
#definimos el rol User y solamente le vamos a pasar la pregunta del usuario que viene desde el chat
def systemPrompt():
    final_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", 
            """
            Eres un asistente de la empresa Algeiba experto en generar consulta de bases de datos SQL para responder preguntas acerca de las ventas.
            No generes consultas para insertar o modificar datos.
            Formatea los números con la región es-AR.
            Formatea los precios con la región es-AR.  
            No generes comentarios adicionales, producirán error en la consulta SQL.
            Si te dan una Region en español traducila a inglés.
            Si te dan un Country (País) en español traducilo a inglés.
            Si te dan un Item Type (Tipo de producto) en español traducilo a inglés.
            Siempre responde en español. 

            #Utiliza el siguiente esquema de base de datos perteneciente al área de ventas:
            
            #La tabla se llama [Sales$] y contiene las siguientes columnas:

                #[Region]: almacena el nombre de las regiones en inglés
                #[Country]: almacena el nombre de los países en inglés
                #[Item Type]: es el nombre del tipo de producto en inglés
                #[Sales Channel]: es el canal de venta Online ó Offline
                #[Order Priority]: determina la prioridad de venta por orden alfabético
                #[Order Date]: fecha de compra con el formato MM/dd/yyyy
                #[Order ID]: Id de la orden de compra
                #[Ship Date]: fecha de envío con el formato MM/dd/yyyy
                #[Units Sold]: unidades vendidas
                #[Unit Price]: precio unitario del producto
                #[Unit Cost]: precio costo unitario del producto
                #[Total Revenue]: ingresos totales por producto
                #[Total Cost]: costo total
                #[Total Profit]: beneficio total de la venta            
            """
            ),
            ("user", "{question}\n "),
        ]
    )

    return final_prompt

def _handle_error(error) -> str:
    return str(error)[216:]

#procesamos la consulta
def queryProcessing(question):
    db_engine = CreateSqlEngine()
    db = SQLDatabase(db_engine)
    llm = InitializeAzureOpenAI()
    sql_toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    sql_toolkit.get_tools()

    #creamos el agente SQL que nos provee LangChain
    sqldb_agent = create_sql_agent(
        llm=llm,
        toolkit=sql_toolkit,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
    )

    try: 
        # a veces el agente se confunde y a pesar de encontrar la respuesta falla, por eso, está el try cath
        prompt = systemPrompt()
        return sqldb_agent.run(prompt.format(
            question=question
        ))  
    except ValueError as ex:
        return _handle_error(str(ex)) 

#por acá comienza todo el camino del procesamiento de este Azure Function
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)
@app.route(route="OrchestratorFunction", methods=['POST'])
def OrchestratorFunction(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    req_body = req.get_json()
    question = req_body.get('question')
    if question:
        try:
            answer = queryProcessing(question)
            return func.HttpResponse(answer, status_code=200)

        except ValueError as excValue:
            return func.HttpResponse(f"Value error: {str(excValue)}")
        except TypeError as typeValue:
            return func.HttpResponse(f"Type error: {str(typeValue)}")
    else:
        return func.HttpResponse("Invalid request", status_code=400)