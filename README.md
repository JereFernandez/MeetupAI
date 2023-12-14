# MeetupAI
Chatbot with bot framework .NET and LangChain Python library

# Arquitectura
Esta pensada para funcionar en Azure y con la licencia Enterprise, o sea, los 150USD mensuales que tenemos nos alcanza para levantar la arquitectura. Si tenes dudas de cómo hacerlo hablame al chat y te ayudo.

# Como recorrer el código
La aplicación .NET está en la carpeta Chatbot y las clases relevantes son: MainDialog.cs y AzFunctionClientService.cs
Fuera de estas clases pueden revisar el código y para comprenderlo tendrán que ver documentación del SDK Bot Framework para .NET

Por otro lado, la parte de Python LangChain se encuentra en la carpeta Orchestrator y toda la lógica se encuentra en function_app.py

Cualquier duda que tengan para levantar la arquitectura o desarrollar su propia aplicación no duden en escribirme.
