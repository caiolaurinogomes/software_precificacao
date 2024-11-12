import os
from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import SQLALCHEMY_DATABASE_URL  # Importando a configuração da string de conexão
from sqlalchemy.exc import SQLAlchemyError

# Criação do aplicativo Flask
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'supersecretkey')  # Pega a secret key de uma variável de ambiente

# Configuração da string de conexão com o banco de dados
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Função para obter uma sessão de banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Modelo de exemplo para guardar os dados
from sqlalchemy import Column, Integer, String

class UserInput(Base):
    __tablename__ = 'user_input'
    id = Column(Integer, primary_key=True, index=True)
    input_data = Column(String, index=True)

# Rota para a página principal
@app.route('/')
def index():
    return render_template('index.html')  # Exemplo de uma página HTML para exibir um formulário

# Rota para o formulário de input
@app.route('/submit', methods=['POST'])
def submit_input():
    user_input = request.form['user_input']
    
    # Usando o banco de dados para salvar o input
    db = next(get_db())
    try:
        new_input = UserInput(input_data=user_input)
        db.add(new_input)
        db.commit()
        db.refresh(new_input)
        return redirect(url_for('index'))  # Redireciona para a página inicial após salvar
    except SQLAlchemyError as e:
        db.rollback()
        return f"Erro ao salvar no banco de dados: {e}"

if __name__ == "__main__":
    # No Azure, não especificamos host e port explicitamente
    app.run(debug=True)  # Para testes locais, você pode manter o debug True
