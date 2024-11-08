import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Senha para conectar ao banco de dados
# Para autenticação do Azure AD, a senha não é usada diretamente aqui
# Utilize um token de autenticação se necessário

# Configuração do banco de dados Azure SQL
DATABASE_URL = (
    "mssql+pyodbc://caio.laurino@push3.com.br@softwareprecificacao.database.windows.net/precificacao_db?"
    "driver=ODBC+Driver+17+for+SQL+Server;"
    "Authentication=ActiveDirectoryPassword;"
    "UID=caio.laurino@push3.com.br;"
    "PWD=Spfc1717!"
)

try:
    # Cria o engine do SQLAlchemy
    engine = create_engine(DATABASE_URL)
except Exception as e:
    print(f"Erro ao criar o engine do banco de dados: {e}")

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

    try:
        yield db
    finally:
        db.close()
