import os

# Configurações do banco de dados Azure SQL
DATABASE_USERNAME = "caio_laurino"  # Nome do usuário SQL
DATABASE_PASSWORD = "Spfc1717!"  # Senha do usuário SQL
DATABASE_SERVER = "softwareprecificacao.database.windows.net"  # Nome do servidor
DATABASE_NAME = "db_precificacao"  # Nome do banco de dados

# String de conexão para autenticação SQL
SQLALCHEMY_DATABASE_URL = (
    f"mssql+pyodbc://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_SERVER}:1433/{DATABASE_NAME}?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
)
