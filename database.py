import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configurações do banco de dados Azure SQL
username = "caio.laurino@push3.com.br"  # Seu e-mail
password = "Spfc1717!"  # Sua senha
server = "softwareprecificacao.database.windows.net"  # Nome do servidor
database = "precificacao_db"  # Nome do banco de dados

# String de conexão para autenticação do Azure Active Directory
DATABASE_URL = (
    f"mssql+pyodbc://{username}:{password}@{server}:1433/"
    f"{database}?driver=ODBC+Driver+18+for+SQL+Server&"
    "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    "Authentication=ActiveDirectoryPassword"
)

# Criação do engine do SQLAlchemy
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

