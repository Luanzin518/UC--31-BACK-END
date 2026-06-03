from flask import Flask, render_template, request
import re

app = Flask(__name__)

@app.route('/')
def cadastro():
    return render_template('index.html')

@app.route('/validacao', methods=['POST'])
def validacao():
 
    nome     = request.form.get('nome', '').strip().title()
    email    = request.form.get('email', '').strip().lower()
    cidade   = request.form.get('cidade', '').strip().title()
    telefone = request.form.get('telefone', '').strip()
    CPF      = request.form.get('CPF', '').strip()
    Estado   = request.form.get('Estado', '').strip().upper()
    Curso    = request.form.get('Curso', '').strip()
    Idade    = request.form.get('Idade', '').strip()
    Senha    = request.form.get('Senha', '').strip()

   
    telefone = re.sub(r'\D', '', telefone)
    CPF      = re.sub(r'\D', '', CPF)

  
    erros = []

    if any(c == '' for c in [nome, email, cidade, telefone, CPF, Estado, Curso, Idade, Senha]):
        erros.append('Preencha todos os campos obrigatórios.')
    else:
        if len(nome) < 8:
            erros.append('Nome inválido.')

        if '@' not in email or '.com' not in email:
            erros.append('E-mail inválido.')

        if not telefone.isdigit() or len(telefone) != 11:
            erros.append('Telefone inválido.')

        if not CPF.isdigit() or len(CPF) != 11:
            erros.append('CPF inválido.')

        if len(cidade) < 3:
            erros.append('Cidade inválida.')

        if len(Estado) != 2 or not Estado.isalpha():
            erros.append('Estado inválido.')

        try:
            if int(Idade) < 16:
                erros.append('Idade inválida.')
        except ValueError:
            erros.append('Idade inválida.')

        if len(Senha) < 8 or not any(c.isdigit() for c in Senha):
            erros.append('Senha muito fraca.')


    return f"""
    <h1>Cadastro realizado com sucesso!</h1>
    <p>Nome: {nome}</p>
    <p>Email: {email}</p>
    <p>Cidade: {cidade}</p>
    <p>Telefone: {telefone}</p>
    <p>CPF: {CPF}</p>
    <p>Estado: {Estado}</p>
    <p>Curso: {Curso}</p>
    <p>Idade: {Idade}</p>
    <a href="/">Voltar</a>
    """

if __name__ == '__main__':
    app.run(debug=True)