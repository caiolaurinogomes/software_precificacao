from flask import render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db
from models import Usuario

login_manager = LoginManager()
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

@login_manager.user_loader
def load_user(user_id):
    db = next(get_db())
    usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
    return User(user_id=usuario.id) if usuario else None

def add_login_routes(app):
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            db = next(get_db())
            usuario = db.query(Usuario).filter(Usuario.username == username).first()
            if usuario and check_password_hash(usuario.password_hash, password):
                login_user(User(user_id=usuario.id))
                flash("Login realizado com sucesso!", "success")
                return redirect(url_for('protected_dashboard'))
            flash("Nome de usuário ou senha inválidos", "danger")
        return render_template('login.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            db = next(get_db())
            if db.query(Usuario).filter(Usuario.username == username).first():
                flash("Nome de usuário já existe.", "danger")
                return redirect(url_for('register'))
            db.add(Usuario(username=username, password_hash=generate_password_hash(password)))
            db.commit()
            flash("Usuário registrado com sucesso!", "success")
            return redirect(url_for('login'))
        return render_template('register.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash("Você foi desconectado.", "info")
        return redirect(url_for('login'))

