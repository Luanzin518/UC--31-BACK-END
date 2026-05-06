from flask import Flask

app = Flask(__name__)

@app.route("/arearestrita/<id>")
def area(id):
    cadeados = {
        "1": " Cadeado Fechado",
        "2": " Cadeado Aberto"
    }

    return cadeados.get(id, "ID inválido")


@app.route("/operacao/<tipo>/<int:op1>/<int:op2>")
def operacao(tipo, op1, op2):
    operacoes = {
        "sum": op1 + op2,
        "sub": op1 - op2,
        "mult": op1 * op2,
        "div": op1 / op2
    }

    return f"Resultado: {operacoes.get(tipo, 'Operação inválida')}"


app.run()