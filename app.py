from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/lanches")
def lanches():
    return render_template("lanche.html")


@app.route("/pedidos")
def pedidos():
    return render_template("pedidos.html")


@app.route("/contato")
def contato():
    return render_template("contato.html")

@app.route("/cardapio")
def sobre():
    return render_template("cardapio.html")


if __name__ == "__main__":
    app.run(debug=True)