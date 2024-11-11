from flask import Flask, request, render_template
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import DATABASE_URL

app = Flask(__name__)

# Conectando ao banco de dados
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Definir uma tabela simples para armazenar o input
class UserInput(Base):
    __tablename__ = 'user_inputs'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    input_data = sqlalchemy.Column(sqlalchemy.String, index=True)

# Criar as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_input = request.form['user_input']
        db = SessionLocal()
        new_input = UserInput(input_data=user_input)
        db.add(new_input)
        db.commit()
        db.close()
        return render_template("index.html", message="Input salvo com sucesso!")

    return render_template("index.html", message="")

if __name__ == "__main__":
    app.run(debug=True)



if __name__ == "__main__":
    # No Azure, não especificamos host e port explicitamente
    app.run()

