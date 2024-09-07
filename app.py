from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pokedex.db'
db = SQLAlchemy(app)

class Pokemon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)

@app.route('/')
def index():
    pokemons = Pokemon.query.all()
    return render_template('index.html', pokemons=pokemons)

@app.route('/adicionar', methods=['GET', 'POST'])
def adicionar():
    if request.method == 'POST':
        nome = request.form['nome']
        tipo = request.form['tipo']
        novo_pokemon = Pokemon(nome=nome, tipo=tipo)
        db.session.add(novo_pokemon)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('adicionar.html')

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    pokemon = Pokemon.query.get_or_404(id)
    if request.method == 'POST':
        pokemon.nome = request.form['nome']
        pokemon.tipo = request.form['tipo']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('editar.html', pokemon=pokemon)

@app.route('/remover/<int:id>')
def remover(id):
    pokemon = Pokemon.query.get_or_404(id)
    db.session.delete(pokemon)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)