from flask import Flask, render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Armazenamento temporário (apenas para fins didáticos, sem banco de dados)
usuario_cadastrado = {
    "nome": None,
    "senha_hash": None
}

# Guarda o nome de quem está logado no momento (também apenas em memória)
usuario_logado = {
    "nome": None
}


@app.route("/", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form["nome"]
        senha = request.form["senha"]

        # Gera o hash da senha e armazena junto com o nome
        usuario_cadastrado["nome"] = nome
        usuario_cadastrado["senha_hash"] = generate_password_hash(senha)

        return redirect(url_for("login"))

    return render_template("cadastro.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    erro = None

    if request.method == "POST":
        nome = request.form["nome"]
        senha = request.form["senha"]

        if nome != usuario_cadastrado["nome"]:
            erro = "Usuário não encontrado."
        elif not check_password_hash(usuario_cadastrado["senha_hash"], senha):
            erro = "Senha inválida."
        else:
            usuario_logado["nome"] = nome
            return redirect(url_for("inicio"))

    return render_template("login.html", erro=erro)


@app.route("/inicio")
def inicio():
    # Se ninguém estiver logado, volta para o login
    if not usuario_logado["nome"]:
        return redirect(url_for("login"))

    return render_template("inicio.html", nome=usuario_logado["nome"])


if __name__ == "__main__":
    app.run(debug=True)