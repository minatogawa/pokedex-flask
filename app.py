from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pokedex.db'
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db = SQLAlchemy(app)

class Pokemon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    imagem_url = db.Column(db.String(200))

# Adicione esta função
def init_db():
    with app.app_context():
        db.create_all()

def salvar_imagem(imagem):
    if imagem:
        filename = secure_filename(imagem.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        imagem.save(filepath)
        return f'/static/uploads/{filename}'
    return None

@app.route('/')
def index():
    pokemons = Pokemon.query.all()
    return render_template('index.html', pokemons=pokemons)

@app.route('/adicionar', methods=['GET', 'POST'])
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
        
        novo_pokemon = Pokemon(nome=nome, tipo=tipo, imagem_url=imagem_url)
        db.session.add(novo_pokemon)
        db.session.commit()
        flash('Pokémon adicionado com sucesso!', 'success')
        return redirect(url_for('index'))
    return render_template('adicionar.html')

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    pokemon = Pokemon.query.get_or_404(id)
    if request.method == 'POST':
        pokemon.nome = request.form['nome']
        pokemon.tipo = request.form['tipo']
        imagem_url = request.form['imagem_url']
        
        if 'imagem' in request.files:
            imagem = request.files['imagem']
            if imagem.filename != '':
                imagem_url = salvar_imagem(imagem)
        
        if not imagem_url:
            flash('Por favor, forneça uma imagem ou URL válida.', 'error')
            return render_template('editar.html', pokemon=pokemon)
        
        pokemon.imagem_url = imagem_url
        db.session.commit()
        flash('Pokémon atualizado com sucesso!', 'success')
        return redirect(url_for('index'))
    return render_template('editar.html', pokemon=pokemon)

@app.route('/remover/<int:id>')
def remover(id):
    pokemon = Pokemon.query.get_or_404(id)
    db.session.delete(pokemon)
    db.session.commit()
    flash('Pokémon removido com sucesso!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()  # Chame a função init_db aqui
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)