from flask import Flask, render_template, request, redirect, url_for, flash, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pokedex.db'
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'  # Mude isso para uma chave secreta real
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Pokemon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    imagem_url = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('pokemons', lazy=True))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def init_db():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='teste').first():
            user = User(username='teste')
            user.set_password('senha123')
            db.session.add(user)
            db.session.commit()

            # Adicionar alguns Pokémon de exemplo para o usuário de teste
            pokemons = [
                Pokemon(nome='Pikachu', tipo='Elétrico', user_id=user.id),
                Pokemon(nome='Charmander', tipo='Fogo', user_id=user.id),
                Pokemon(nome='Squirtle', tipo='Água', user_id=user.id)
            ]
            db.session.add_all(pokemons)
            db.session.commit()

def salvar_imagem(imagem):
    if imagem:
        filename = secure_filename(imagem.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        imagem.save(filepath)
        return url_for('static', filename=f'uploads/{filename}', _external=True)
    return None

@app.route('/')
@login_required
def index():
    pokemons = Pokemon.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', pokemons=pokemons)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Usuário ou senha inválidos.', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/adicionar', methods=['GET', 'POST'])
@login_required
def adicionar():
    if request.method == 'POST':
        nome = request.form['nome']
        tipo = request.form['tipo']
        imagem_url = request.form['imagem_url']
        
        if 'imagem' in request.files:
            imagem = request.files['imagem']
            if imagem.filename != '':
                imagem_url = salvar_imagem(imagem)
        
        if not imagem_url:
            flash('Por favor, forneça uma imagem ou URL válida.', 'error')
            return render_template('adicionar.html')
        
        novo_pokemon = Pokemon(nome=nome, tipo=tipo, imagem_url=imagem_url, user_id=current_user.id)
        db.session.add(novo_pokemon)
        db.session.commit()
        flash('Pokémon adicionado com sucesso!', 'success')
        return redirect(url_for('index'))
    return render_template('adicionar.html')

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    pokemon = Pokemon.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    if request.method == 'POST':
        pokemon.nome = request.form['nome']
        pokemon.tipo = request.form['tipo']
        
        if 'imagem' in request.files and request.files['imagem'].filename != '':
            imagem = request.files['imagem']
            imagem_url = salvar_imagem(imagem)
            if imagem_url:
                pokemon.imagem_url = imagem_url
        elif request.form['imagem_url']:
            pokemon.imagem_url = request.form['imagem_url']
        
        db.session.commit()
        flash('Pokémon atualizado com sucesso!', 'success')
        return redirect(url_for('index'))
    return render_template('editar.html', pokemon=pokemon)

@app.route('/remover/<int:id>')
@login_required
def remover(id):
    pokemon = Pokemon.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(pokemon)
    db.session.commit()
    flash('Pokémon removido com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        user = User.query.filter_by(username=username).first()
        if user:
            flash('Nome de usuário já existe. Por favor, escolha outro.', 'error')
        elif password != confirm_password:
            flash('As senhas não coincidem.', 'error')
        else:
            new_user = User(username=username)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registro realizado com sucesso! Faça login para continuar.', 'success')
            return redirect(url_for('login'))

    return render_template('registro.html')

if __name__ == '__main__':
    init_db()  # Chame a função init_db aqui
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)