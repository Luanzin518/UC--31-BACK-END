from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/recebedados', methods=['POST'])
def recebedados():
    nome = request.form.get('nome')
    email = request.form.get('email')

    return "{} e {}".format(nome, email)

if __name__ == '__main__':
    app.run(debug=True)




app = Flask(__name__)

@app.route('/formregistrar')
def formregistrar():
    return render_template('registrar.html')


@app.route('/registrar', methods=['POST'])
def registrar():
    usuario = request.form['usuario']
    email = request.form['email']
    senha = request.form['senha']
    confirmar = request.form['confirmar']

    if senha == confirmar:
        return "Usuário registrado com sucesso"
    else:
        return "As senhas não conferem"


if __name__ == '__main__':
    app.run(debug=True)