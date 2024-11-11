# config.py

import os

# Configurações de conexão ao banco de dados
DATABASE_URL = (
    f"mssql+pyodbc://caio.laurino@push3.com.br:{os.getenv('DB_PASSWORD')}@softwareprecificacao.database.windows.net:1433/"
    "precificacao_db?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    "Authentication=ActiveDirectoryPassword"
)
