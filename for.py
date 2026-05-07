from flask import Flask, render_template

app = Flask(__name__)

@app.route('/pizzaria/<sabor>')
def pizzaria(sabor):
    if sabor == "calabresa":
        return render_template("calabresa.html")
    elif sabor == "margherita":
        return render_template("margherita.html")
    elif sabor == "frango":
        return render_template("frango.html")
    else:
        return render_template("erro.html")

if __name__ == '__main__':
    app.run(debug=True)