from flask import (
    Flask,
    render_template,
    session,
    redirect,
    url_for,
    request,
    flash
)


from datetime import timedelta

app = Flask(__name__)

app.config['SECRET_KEY'] = 'chave-aula38-uc31'

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)


PRODUTOS = [
    {'id': 1, 'nome': 'Notebook',  'preco': 3500.00},
    {'id': 2, 'nome': 'Mouse',     'preco': 80.00},
    {'id': 3, 'nome': 'Teclado',   'preco': 150.00},
    {'id': 4, 'nome': 'Monitor',   'preco': 1200.00},
    {'id': 5, 'nome': 'Headphone', 'preco': 250.00},
]

@app.route('/')
def inicio():

    nome    = session.get('nome', None)
    tema    = session.get('tema', 'claro')
    idioma  = session.get('idioma', 'pt')
    visitas = session.get('visitas', 0)

    session['visitas'] = visitas + 1

    return render_template(
        'inicio.html',
        nome=nome,
        tema=tema,
        idioma=idioma,
        visitas=session['visitas']
    )


@app.route('/personalizar', methods=['GET', 'POST'])
def personalizar():

    if request.method == 'POST':

        nome = request.form.get('nome', '').strip().title()
        tema = request.form.get('tema', 'claro')
        idioma = request.form.get('idioma', 'pt')
        lembrar = request.form.get('lembrar')

        if not nome:
            flash('Informe seu nome.', 'erro')
            return redirect(url_for('personalizar'))

        session['nome'] = nome
        session['tema'] = tema
        session['idioma'] = idioma

        if lembrar == 'sim':
            session.permanent = True
        else:
            session.permanent = False

        flash(f'Preferências salvas, {nome}!', 'sucesso')

        return redirect(url_for('inicio'))

    return render_template(
        'personalizar.html',
        nome_atual=session.get('nome', ''),
        tema_atual=session.get('tema', 'claro'),
        idioma_atual=session.get('idioma', 'pt')
    )


@app.route('/limpar-nome')
def limpar_nome():

    session.pop('nome', None)

    flash('Nome removido da session.', 'info')

    return redirect(url_for('inicio'))


@app.route('/limpar-tudo')
def limpar_tudo():

    session.clear()

    flash('Toda a session foi limpa.', 'info')

    return redirect(url_for('inicio'))

@app.route('/carrinho')
def carrinho():

    carrinho_atual = session.get('carrinho', [])

    total = sum(item['preco'] * item['qtd'] for item in carrinho_atual)

    return render_template(
        'carrinho.html',
        produtos=PRODUTOS,
        carrinho=carrinho_atual,
        total=total
    )


@app.route('/carrinho/adicionar/<int:produto_id>')
def adicionar_ao_carrinho(produto_id):

    produto = next(
        (p for p in PRODUTOS if p['id'] == produto_id),
        None
    )

    if not produto:
        flash('Produto não encontrado.', 'erro')
        return redirect(url_for('carrinho'))

    carrinho_atual = session.get('carrinho', [])

    item_existente = next(
        (item for item in carrinho_atual if item['id'] == produto_id),
        None
    )

    if item_existente:
        item_existente['qtd'] += 1

    else:
        carrinho_atual.append({
            'id': produto['id'],
            'nome': produto['nome'],
            'preco': produto['preco'],
            'qtd': 1
        })

    session['carrinho'] = carrinho_atual

    session.modified = True

    flash(f'{produto["nome"]} adicionado ao carrinho!', 'sucesso')

    return redirect(url_for('carrinho'))



@app.route('/carrinho/remover/<int:produto_id>')
def remover_do_carrinho(produto_id):

    carrinho_atual = session.get('carrinho', [])

    novo_carrinho = [
        item for item in carrinho_atual
        if item['id'] != produto_id
    ]

    session['carrinho'] = novo_carrinho

    session.modified = True

    flash('Produto removido.', 'info')

    return redirect(url_for('carrinho'))


@app.route('/carrinho/limpar')
def limpar_carrinho():

    session.pop('carrinho', None)

    session.modified = True

    flash('Carrinho esvaziado!', 'info')

    return redirect(url_for('carrinho'))


@app.route('/debug-session')
def debug_session():

    conteudo = dict(session)

    html = '<h1>Conteúdo da Session</h1><ul>'

    for chave, valor in conteudo.items():
        html += f'<li><strong>{chave}</strong>: {valor}</li>'

    html += '</ul>'
    html += '<a href="/">Voltar</a>'

    return html

@app.route('/carrinho/adicionar/webcam')
def adicionar_webcam():
    carrinho = session.get('carrinho', [])
    novo_produto = {'id': 6, 'nome': 'Webcam', 'preco': 300.00}
    carrinho.append(novo_produto)
    session['carrinho'] = carrinho
    flash('Webcam A adicionada ao carrinho!', 'success')
    return redirect(url_for('carrinho'))

@app.route('/personalizar', methods=['GET', 'POST'])
def personalizar():
    if request.method == 'POST':
        session['nome'] = request.form.get('nome')
        session['tema'] = request.form.get('tema')
        session['cor']  = request.form.get('cor', 'azul')  # nova linha
        flash('Preferências salvas!', 'success')
        return redirect(url_for('inicio'))
    return render_template('preferencias.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Você saiu com sucesso. Até logo!', 'info')
    return redirect(url_for('inicio'))

@app.route('/visitas')
def visitas():
    total = session.get('visitas', 0)
    return f'Você visitou este site {total} vezes.'




# ── rotas ──────────────────────────────────────────────

@app.route('/favoritos')
def favoritos():
    """Exibe a lista de produtos favoritos."""
    favoritos = session.get('favoritos', [])
    return render_template('favoritos.html', favoritos=favoritos)


@app.route('/favoritos/adicionar/<int:produto_id>')
def adicionar_favorito(produto_id):
    """Adiciona um produto aos favoritos pelo ID."""
    # Catálogo de produtos disponíveis
    produtos = [
        {'id': 1, 'nome': 'Teclado',   'preco': 150.00},
        {'id': 2, 'nome': 'Mouse',     'preco':  80.00},
        {'id': 3, 'nome': 'Monitor',   'preco': 900.00},
        {'id': 4, 'nome': 'Headset',   'preco': 200.00},
        {'id': 5, 'nome': 'Webcam A',  'preco': 300.00},
    ]

    produto = next((p for p in produtos if p['id'] == produto_id), None)

    if not produto:
        flash('Produto não encontrado.', 'danger')
        return redirect(url_for('inicio'))

    favoritos = session.get('favoritos', [])

    # Evita duplicatas
    if any(f['id'] == produto_id for f in favoritos):
        flash(f'"{produto["nome"]}" já está nos favoritos.', 'warning')
    else:
        favoritos.append(produto)
        session['favoritos'] = favoritos
        session.modified = True
        flash(f'"{produto["nome"]}" adicionado aos favoritos!', 'success')

    return redirect(url_for('favoritos'))


@app.route('/favoritos/remover/<int:produto_id>')
def remover_favorito(produto_id):
    """Remove um produto dos favoritos pelo ID."""
    favoritos = session.get('favoritos', [])
    favoritos_atualizados = [f for f in favoritos if f['id'] != produto_id]

    if len(favoritos_atualizados) == len(favoritos):
        flash('Produto não estava nos favoritos.', 'warning')
    else:
        session['favoritos'] = favoritos_atualizados
        session.modified = True
        flash('Produto removido dos favoritos.', 'info')

    return redirect(url_for('favoritos'))


@app.route('/favoritos/limpar')
def limpar_favoritos():
    """Remove todos os favoritos de uma vez."""
    session.pop('favoritos', None)
    flash('Lista de favoritos limpa.', 'info')
    return redirect(url_for('favoritos'))


if __name__ == '__main__':
    app.run(debug=True)