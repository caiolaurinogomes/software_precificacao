import os
from flask import Flask, render_template, redirect, url_for
from dash import Dash
import dash_bootstrap_components as dbc
from layout import create_layout
from callbacks import register_callbacks
from login import login_manager, add_login_routes
from flask_login import login_required  # Import necessário para proteger rotas
from database import Base, engine  # Importe Base e engine de database.py
from models import Input as UserInput

# Configuração do aplicativo Flask
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'supersecretkey')  # Pega a secret key de uma variável de ambiente

# Define a pasta de upload
app.config['UPLOAD_FOLDER'] = 'uploads'

# Cria as tabelas no banco de dados
try:
    Base.metadata.create_all(bind=engine)  # Cria as tabelas na primeira execução
except Exception as e:
    print(f"Erro ao conectar ao banco de dados: {e}")

# Inicializa o login manager com o app
login_manager.init_app(app)

# Adiciona as rotas de login
add_login_routes(app)

# Inicializa o aplicativo Dash
dash_app = Dash(__name__, server=app, url_base_pathname='/dashboard/', external_stylesheets=[dbc.themes.BOOTSTRAP])

# Configura o layout do aplicativo Dash
dash_app.layout = create_layout()

# Registra os callbacks
register_callbacks(dash_app)

# Rota principal do Flask para a página inicial
@app.route('/')
def index():
    return render_template('index.html')  # Renderiza o arquivo index.html

# Modifica a rota para redirecionar para o login caso não esteja autenticado
@app.route('/dashboard/')
@login_required
def protected_dashboard():
    # Redireciona para o Dash
    return redirect('/dashboard')  # Redireciona para o Dash diretamente

if __name__ == "__main__":
    # No Azure, não especificamos host e port explicitamente
    app.run()


if __name__ == "__main__":
    # No Azure, não especificamos host e port explicitamente
    app.run()

