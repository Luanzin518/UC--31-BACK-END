from flask import Flask, render_template

app = Flask(__name__)

@app.route('/login')
def login():
    nome = "Luan"  # aqui você pode trocar pelo nome que quiser
    return render_template('login.html', nome=nome)

if __name__ == '__main__':
    app.run(debug=True)