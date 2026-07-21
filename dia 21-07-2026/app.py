from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)

ARQUIVO = 'livros.json'


def ler_livros():
    if not os.path.exists(ARQUIVO):
        with open(ARQUIVO, 'w') as f:
            json.dump([], f)
    with open(ARQUIVO, 'r') as f:
        return json.load(f)


def salvar_livros(livros):
    with open(ARQUIVO, 'w') as f:
        json.dump(livros, f, indent=4)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        autor = request.form.get('autor')
        ano = request.form.get('ano')
        categoria = request.form.get('categoria')
        quantidade = request.form.get('quantidade')

        if not titulo or not autor or not ano or not categoria or not quantidade:
            return render_template('cadastro.html', erro='Preencha todos os campos.')

        if not ano.isdigit():
            return render_template('cadastro.html', erro='O ano deve conter apenas números.')

        if not quantidade.isdigit() or int(quantidade) <= 0:
            return render_template('cadastro.html', erro='A quantidade deve ser maior que zero.')

        livros = ler_livros()
        livros.append({
            'titulo': titulo,
            'autor': autor,
            'ano': ano,
            'categoria': categoria,
            'quantidade': int(quantidade)
        })
        salvar_livros(livros)
        return redirect(url_for('listar_livros'))

    return render_template('cadastro.html')


@app.route('/livros')
def listar_livros():
    livros = ler_livros()
    return render_template('livros.html', livros=livros)


@app.route('/buscar', methods=['GET', 'POST'])
def buscar():
    resultado = None
    encontrado = True

    if request.method == 'POST':
        titulo_busca = request.form.get('titulo', '').lower()
        livros = ler_livros()

        for livro in livros:
            if livro['titulo'].lower() == titulo_busca:
                resultado = livro
                break

        if resultado is None:
            encontrado = False

    return render_template('buscar.html', resultado=resultado, encontrado=encontrado)


@app.route('/editar/<int:indice>', methods=['GET', 'POST'])
def editar(indice):
    livros = ler_livros()

    if indice < 0 or indice >= len(livros):
        return redirect(url_for('listar_livros'))

    if request.method == 'POST':
        titulo = request.form.get('titulo')
        autor = request.form.get('autor')
        ano = request.form.get('ano')
        categoria = request.form.get('categoria')
        quantidade = request.form.get('quantidade')

        if not titulo or not autor or not ano or not categoria or not quantidade:
            return render_template('editar.html', livro=livros[indice], indice=indice, erro='Preencha todos os campos.')

        if not ano.isdigit():
            return render_template('editar.html', livro=livros[indice], indice=indice, erro='O ano deve conter apenas números.')

        if not quantidade.isdigit() or int(quantidade) <= 0:
            return render_template('editar.html', livro=livros[indice], indice=indice, erro='A quantidade deve ser maior que zero.')

        livros[indice] = {
            'titulo': titulo,
            'autor': autor,
            'ano': ano,
            'categoria': categoria,
            'quantidade': int(quantidade)
        }
        salvar_livros(livros)
        return redirect(url_for('listar_livros'))

    return render_template('editar.html', livro=livros[indice], indice=indice)


@app.route('/excluir/<int:indice>')
def excluir(indice):
    livros = ler_livros()
    if 0 <= indice < len(livros):
        livros.pop(indice)
        salvar_livros(livros)
    return redirect(url_for('listar_livros'))


if __name__ == '__main__':
    app.run(debug=True)