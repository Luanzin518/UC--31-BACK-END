from flask import Flask, session, redirect, url_for, request, render_template

app = Flask(__name__)
app.secret_key = 'tarefa-session-2025'

@app.route('/')
def index():
    tarefas = session.get('tarefas', [])
    return render_template('index.html', tarefas=tarefas)

@app.route('/adicionar', methods=['POST'])
def adicionar():
    texto = request.form.get('tarefa', '').strip()
    if texto:
        tarefas = session.get('tarefas', [])
        tarefas.append({'texto': texto, 'feita': False})
        session['tarefas'] = tarefas
    return redirect(url_for('index'))

@app.route('/concluir/<int:indice>')
def concluir(indice):
    tarefas = session.get('tarefas', [])
    if 0 <= indice < len(tarefas):
        tarefas[indice]['feita'] = not tarefas[indice]['feita']
        session['tarefas'] = tarefas
    return redirect(url_for('index'))

@app.route('/limpar')
def limpar():
    session.pop('tarefas', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)