import os

# Configurações do banco de dados Azure SQL
DATABASE_USERNAME = "caio.laurino@push3.com.br"  # Seu e-mail
DATABASE_PASSWORD = "Spfc1717!"  # Sua senha
DATABASE_SERVER = "softwareprecificacao.database.windows.net"  # Nome do servidor
DATABASE_NAME = "precificacao_db"  # Nome do banco de dados

# String de conexão para autenticação do Azure Active Directory
SQLALCHEMY_DATABASE_URL = f"mssql+pyodbc://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_SERVER}/{DATABASE_NAME}?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;Authentication=ActiveDirectoryPassword"
