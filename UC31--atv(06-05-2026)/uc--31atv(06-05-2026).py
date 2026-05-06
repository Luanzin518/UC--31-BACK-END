from flask import Flask

app = Flask(__name__)


@app.route('/ola/<nome>')
def ola(nome):
    return f'Olá, {nome}! Seja bem-vinda ao sistema.'


@app.route('/calculo/<int:n1>/<int:n2>')
def calculo(n1, n2):
    soma = n1 + n2
    return f'A soma de {n1} + {n2} é {soma}'

@app.route('/idade/<nome>/<int:idade>')
def idade(nome, idade):
    if idade >= 18:
        return f'{nome} é maior de idade.'
    else:
        return f'{nome} é menor de idade.'


@app.route('/produto/<nome>/<float:preco>')
def produto(nome, preco):
    return f'O produto {nome} custa R$ {preco:.2f}'


@app.route('/repetir/<palavra>/<int:vezes>')
def repetir(palavra, vezes):
    return (palavra + ' ') * vezes

app.run(debug=True)