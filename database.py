import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from getpass import getpass  # Importa a função getpass para solicitar a senha

# Solicita a senha do usuário de forma segura
password = getpass("Digite sua senha para conectar ao banco de dados: ")

# Configuração do banco de dados Azure SQL
DATABASE_URL = f"mssql+pyodbc://caio.laurino:{password}@softwareprecificacao.database.windows.net/precificacao_db?driver=ODBC+Driver+17+for+SQL+Server"

# Cria o engine do SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para definir as tabelas
Base = declarative_base()

# Função para obter uma sessão de banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
