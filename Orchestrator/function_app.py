import azure.functions as func
import logging
from langchain import OpenAI
from langchain.chains import SQLDatabaseSequentialChain
from langchain.chat_models import AzureChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from langchain.agents import AgentType, create_sql_agent
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_toolkits.sql.toolkit import SQLDatabaseToolkit


os.environ["OPENAI_API_TYPE"]="azure"
os.environ["OPENAI_API_VERSION"]="2023-07-01-preview"
os.environ["OPENAI_API_BASE"]="" # Your Azure OpenAI resource endpoint
os.environ["OPENAI_API_KEY"]="" # Your Azure OpenAI resource key
os.environ["OPENAI_CHAT_MODEL"]="gpt-35-turbo-16k" # Use name of deployment

os.environ["SQL_SERVER"]="" # Your az SQL server name
os.environ["SQL_DB"]="retailshop"
os.environ["SQL_USERNAME"]="" # SQL server username 
os.environ["SQL_PWD"]="{<password>}" # SQL server password 


def CreateSqlEngine():
    driver = '{ODBC Driver 17 for SQL Server}'
    odbc_str = 'mssql+pyodbc:///?odbc_connect=' \
                'Driver='+driver+ \
                ';Server=tcp:' + os.getenv("SQL_SERVER")+'.database.windows.net;PORT=1433' + \
                ';DATABASE=' + os.getenv("SQL_DB") + \
                ';Uid=' + os.getenv("SQL_USERNAME")+ \
                ';Pwd=' + os.getenv("SQL_PWD") + \
                ';Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'

    return create_engine(odbc_str)


def InitializeOpenAI():
    llm = AzureChatOpenAI(model=os.getenv("OPENAI_CHAT_MODEL"),
                      deployment_name=os.getenv("OPENAI_CHAT_MODEL"),
                      temperature=0)
    
    return llm

def systemPrompt():
    final_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", 
            """
            You are a helpful AI assistant expert in querying SQL Database to find answers to user's question about Categories, Products and Orders.
            """
            ),
            ("user", "{question}\n ai: "),
        ]
    )

    return final_prompt

def createSqlAgent():
    db = SQLDatabase(CreateSqlEngine)
    llm = InitializeOpenAI()
    sql_toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    sql_toolkit.get_tools()

    sqldb_agent = create_sql_agent(
        llm=llm,
        toolkit=sql_toolkit,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )

    sqldb_agent.run(systemPrompt.format(
            question="Quantity of kitchen products sold last month?"
    ))  
    

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)
@app.route(route="OrchestratorFunction")
def OrchestratorFunction(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )