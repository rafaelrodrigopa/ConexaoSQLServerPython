import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

driver = os.getenv("DB_DRIVER")
server = os.getenv("DB_SERVER")
database = os.getenv("DB_NAME")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")

odbc_str = (
    f"DRIVER={{{driver}}};"
    f"SERVER={server};"
    f"DATABASE={database};"
    f"UID={user};"
    f"PWD={password};"
    "TrustServerCertificate=yes;"
)

#print("SERVER:", os.getenv("DB_SERVER"))

engine = create_engine(
    f"mssql+pyodbc:///?odbc_connect={quote_plus(odbc_str)}"
)


try:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    print("Conexão com o SQL Server realizada com sucesso")
except SQLAlchemyError as e:
    print("Erro ao conectar ao banco de dados:")
    print(str(e))