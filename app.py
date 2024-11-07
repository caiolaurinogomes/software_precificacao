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
app.secret_key = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'uploads'

Base.metadata.create_all(bind=engine)  # Cria as tabelas na primeira execução

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
    app.run(host='0.0.0.0', port=5001)
