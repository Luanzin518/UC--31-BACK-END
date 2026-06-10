from flask import Flask, render_template, request, redirect, url_for, make_response

app = Flask(__name__)

@app.route("/")
def inicio():
    nome = request.cookies.get("nome", "")
    email = request.cookies.get("email", "")
    tema = request.cookies.get("tema", "claro")
    return render_template("inicio.html", nome=nome, email=email, tema=tema)

@app.route("/salvar", methods=["POST"])
def salvar():
    resposta = make_response(redirect(url_for("inicio")))
    resposta.set_cookie("nome", request.form.get("nome", ""),)
    resposta.set_cookie("email", request.form.get("email", ""), )
    return resposta

@app.route("/tema/<escolha>")
def tema(escolha):
    resposta = make_response(redirect(url_for("inicio")))
    resposta.set_cookie("tema", escolha,)
    return resposta

@app.route("/limpar")
def limpar():
    resposta = make_response(redirect(url_for("inicio")))
    resposta.delete_cookie("nome")
    resposta.delete_cookie("email")
    return resposta

if __name__ == "__main__":
    app.run(debug=True)