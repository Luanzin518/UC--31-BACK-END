"""
CineRepertório — UC31: Desenvolvimento Web com Flask
Aplicação web de repertórios socioculturais (filmes) para a redação do ENEM.

Armazenamento: arquivos JSON em /data (sem banco de dados).
Módulos: contas.py (login, cadastro e A2F) e ia.py (assistente de redação).
CRUD completo: anotações de repertório do usuário (criar, ler, editar, excluir).
O catálogo de filmes é somente leitura e se renova sozinho a cada dia
(seleção rotativa por data), sem edição manual.
"""

import json
import os
import random
import re
import unicodedata
from datetime import date, datetime
from functools import wraps
from urllib.parse import quote_plus

from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

import contas
import ia

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
FILMES_JSON = os.path.join(DATA_DIR, "filmes.json")
ANOTACOES_JSON = os.path.join(DATA_DIR, "anotacoes.json")

app = Flask(__name__)
app.secret_key = os.environ.get("CINE_SECRET", "cinerepertorio-uc31")

PARTES = ["introducao", "desenvolvimento", "conclusao"]
ROTULO_PARTE = {
    "introducao": "Introdução",
    "desenvolvimento": "Desenvolvimento",
    "conclusao": "Conclusão",
}


# --------------------------------------------------------------------------
# Camada de persistência (JSON)
# --------------------------------------------------------------------------
def ler_json(caminho, padrao=None):
    """Lê um arquivo JSON e devolve uma lista. Nunca quebra a aplicação."""
    if padrao is None:
        padrao = []
    if not os.path.exists(caminho):
        return padrao
    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except (json.JSONDecodeError, OSError):
        return padrao


def gravar_json(caminho, dados):
    """Grava a lista recebida no arquivo JSON, formatada e em UTF-8."""
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)


def listar_filmes():
    return ler_json(FILMES_JSON)


def buscar_filme(filme_id):
    return next((f for f in listar_filmes() if f["id"] == filme_id), None)


def listar_anotacoes():
    return ler_json(ANOTACOES_JSON)


def anotacoes_do_usuario():
    usuario = session.get("usuario")
    if not usuario:
        return []
    return [a for a in listar_anotacoes() if a.get("usuario_id") == usuario["id"]]


def gerar_id(texto, existentes):
    """Cria um identificador único em formato slug (ex.: 'cidade-de-deus')."""
    normalizado = unicodedata.normalize("NFKD", texto or "item")
    normalizado = normalizado.encode("ascii", "ignore").decode("ascii").lower()
    slug = re.sub(r"[^a-z0-9]+", "-", normalizado).strip("-") or "item"
    candidato, contador = slug, 2
    while candidato in existentes:
        candidato = f"{slug}-{contador}"
        contador += 1
    return candidato


def temas_disponiveis():
    temas = {tema for filme in listar_filmes() for tema in filme.get("temas", [])}
    return sorted(temas, key=lambda t: t.lower())


def selecao_do_dia(filmes, quantidade=12):
    """Catálogo que se renova sozinho: a vitrine muda a cada dia.

    Usa a data como semente do sorteio, então todos os visitantes veem a
    mesma seleção no mesmo dia e uma seleção diferente no dia seguinte —
    sem ninguém precisar editar o catálogo.
    """
    if not filmes:
        return []
    sorteio = random.Random(date.today().toordinal())
    copia = list(filmes)
    sorteio.shuffle(copia)
    return copia[:quantidade]


# --------------------------------------------------------------------------
# Utilidades de apresentação
# --------------------------------------------------------------------------
def lojas(titulo):
    """Links de compra/aluguel do filme nas principais lojas digitais."""
    termo = quote_plus(titulo)
    return [
        {"nome": "Prime Video", "url": f"https://www.primevideo.com/search?phrase={termo}"},
        {"nome": "Apple TV", "url": f"https://tv.apple.com/search?term={termo}"},
        {"nome": "Google Play", "url": f"https://play.google.com/store/search?q={termo}&c=movies"},
    ]


def imdb_url(titulo, ano):
    return f"https://www.imdb.com/find/?q={quote_plus(f'{titulo} {ano}')}"


@app.context_processor
def injetar_globais():
    """Disponibiliza funções e dados para todos os templates."""
    return {
        "lojas": lojas,
        "imdb_url": imdb_url,
        "rotulo_parte": ROTULO_PARTE,
        "ano_atual": datetime.now().year,
        "usuario": session.get("usuario"),
        "perguntas_ia": ia.PERGUNTAS_SUGERIDAS[:4],
        "atualizado_em": date.today().strftime("%d/%m/%Y"),
    }


@app.template_filter("cartaz")
def filtro_cartaz(valor):
    """Aceita URL externa ou nome de arquivo local em /static/img."""
    if not valor:
        return ""
    if valor.startswith("http"):
        return valor
    return url_for("static", filename=f"img/{valor}")


def login_obrigatorio(view):
    """Protege as rotas que dependem de uma conta ativa."""

    @wraps(view)
    def envolvida(*args, **kwargs):
        if not session.get("usuario"):
            flash("Entre na sua conta para acessar esta página.", "danger")
            return redirect(url_for("entrar", proxima=request.path))
        return view(*args, **kwargs)

    return envolvida


# --------------------------------------------------------------------------
# Rota 1 — Página inicial (GET)
# --------------------------------------------------------------------------
@app.route("/")
def index():
    filmes = listar_filmes()
    destaques = selecao_do_dia(filmes, 10)
    esteira_a = filmes[: len(filmes) // 2]
    esteira_b = filmes[len(filmes) // 2 :]
    return render_template(
        "index.html",
        titulo_pagina="Início",
        destaques=destaques,
        esteira_a=esteira_a,
        esteira_b=esteira_b,
        total=len(filmes),
        total_temas=len(temas_disponiveis()),
    )


# --------------------------------------------------------------------------
# Rota 2 — Catálogo de filmes com busca, filtro e ordenação (GET)
# --------------------------------------------------------------------------
@app.route("/filmes")
def filmes_lista():
    busca = (request.args.get("busca") or "").strip().lower()
    tema = request.args.get("tema") or ""
    parte = request.args.get("parte") or ""
    ordem = request.args.get("ordem") or "imdb"

    resultado = listar_filmes()
    if busca:
        resultado = [
            f
            for f in resultado
            if busca in f["titulo"].lower()
            or busca in f["diretor"].lower()
            or any(busca in t.lower() for t in f.get("temas", []))
        ]
    if tema:
        resultado = [f for f in resultado if tema in f.get("temas", [])]
    if parte:
        resultado = [f for f in resultado if f.get("parte") == parte]

    if ordem == "ano":
        resultado.sort(key=lambda f: f.get("ano", 0), reverse=True)
    elif ordem == "titulo":
        resultado.sort(key=lambda f: f["titulo"].lower())
    else:
        resultado.sort(key=lambda f: f.get("imdb", 0), reverse=True)

    return render_template(
        "filmes.html",
        titulo_pagina="Filmes",
        filmes=resultado,
        temas=temas_disponiveis(),
        busca=busca,
        tema=tema,
        parte=parte,
        ordem=ordem,
        partes=PARTES,
    )


# --------------------------------------------------------------------------
# Rota 3 — Detalhe do filme, com repertório e links de compra (GET)
# --------------------------------------------------------------------------
@app.route("/filmes/<filme_id>")
def filme_detalhe(filme_id):
    filme = buscar_filme(filme_id)
    if filme is None:
        return render_template("404.html", titulo_pagina="Não encontrado"), 404
    relacionados = [
        f
        for f in listar_filmes()
        if f["id"] != filme_id and set(f.get("temas", [])) & set(filme.get("temas", []))
    ][:6]
    anotacoes = [a for a in anotacoes_do_usuario() if a.get("filme_id") == filme_id]
    return render_template(
        "detalhe.html",
        titulo_pagina=filme["titulo"],
        filme=filme,
        relacionados=relacionados,
        anotacoes=anotacoes,
    )


# --------------------------------------------------------------------------
# Rota 4 — Criar conta (GET + POST) — CREATE de usuário
# --------------------------------------------------------------------------
@app.route("/conta/criar", methods=["GET", "POST"])
def criar_conta():
    if request.method == "POST":
        erros = contas.validar_cadastro(request.form)
        if erros:
            for erro in erros:
                flash(erro, "danger")
            return render_template(
                "criar_conta.html", titulo_pagina="Criar conta", form=request.form
            )
        usuario = contas.criar_usuario(request.form)
        if usuario["a2f"]:
            codigo = contas.gerar_codigo(usuario["email"])
            session["a2f_email"] = usuario["email"]
            session["a2f_proxima"] = url_for("index")
            flash("Conta criada. Enviamos um código de verificação para o seu e-mail.", "success")
            return render_template(
                "verificar.html",
                titulo_pagina="Verificação em duas etapas",
                email=usuario["email"],
                codigo_demo=codigo,
            )
        session["usuario"] = contas.dados_publicos(usuario)
        flash(f"Bem-vindo(a), {usuario['nome']}! Conta criada com sucesso.", "success")
        return redirect(url_for("index"))

    return render_template("criar_conta.html", titulo_pagina="Criar conta", form={})


# --------------------------------------------------------------------------
# Rota 5 — Entrar / trocar de conta (GET + POST)
# --------------------------------------------------------------------------
@app.route("/conta/entrar", methods=["GET", "POST"])
def entrar():
    proxima = request.values.get("proxima") or url_for("index")
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        senha = request.form.get("senha") or ""
        usuario = contas.buscar_por_email(email)
        if not usuario or not contas.senha_confere(usuario, senha):
            flash("E-mail ou senha incorretos.", "danger")
            return render_template("entrar.html", titulo_pagina="Entrar", email=email, proxima=proxima)

        if usuario["a2f"]:
            codigo = contas.gerar_codigo(usuario["email"])
            session["a2f_email"] = usuario["email"]
            session["a2f_proxima"] = proxima
            return render_template(
                "verificar.html",
                titulo_pagina="Verificação em duas etapas",
                email=usuario["email"],
                codigo_demo=codigo,
            )

        session["usuario"] = contas.dados_publicos(usuario)
        flash(f"Olá de novo, {usuario['nome']}!", "success")
        return redirect(proxima)

    return render_template("entrar.html", titulo_pagina="Entrar", email="", proxima=proxima)


# --------------------------------------------------------------------------
# Rota 6 — Verificar código de dois fatores (POST) e sair (GET)
# --------------------------------------------------------------------------
@app.route("/conta/verificar", methods=["POST"])
def verificar_codigo():
    email = session.get("a2f_email")
    if not email:
        flash("Sessão de verificação expirada. Entre novamente.", "danger")
        return redirect(url_for("entrar"))

    ok, mensagem = contas.validar_codigo(email, request.form.get("codigo"))
    if not ok:
        flash(mensagem, "danger")
        return render_template(
            "verificar.html", titulo_pagina="Verificação em duas etapas", email=email, codigo_demo=""
        )

    usuario = contas.buscar_por_email(email)
    session["usuario"] = contas.dados_publicos(usuario)
    proxima = session.pop("a2f_proxima", url_for("index"))
    session.pop("a2f_email", None)
    flash("Verificação concluída. Sua conta está protegida com dois fatores.", "success")
    return redirect(proxima)


@app.route("/conta/sair")
def sair():
    session.pop("usuario", None)
    flash("Você saiu da conta.", "success")
    return redirect(url_for("index"))


# --------------------------------------------------------------------------
# Rota 7 — Anotações de repertório: listar e criar (GET + POST)
# --------------------------------------------------------------------------
@app.route("/anotacoes", methods=["GET", "POST"])
@login_obrigatorio
def anotacoes():
    filmes = listar_filmes()
    if request.method == "POST":
        filme_id = request.form.get("filme_id", "")
        texto = (request.form.get("texto") or "").strip()
        parte = request.form.get("parte", "introducao")
        erros = []
        if not buscar_filme(filme_id):
            erros.append("Selecione um filme válido.")
        if len(texto) < 15:
            erros.append("A anotação deve ter pelo menos 15 caracteres.")
        if parte not in PARTES:
            erros.append("Selecione em qual parágrafo o repertório será usado.")
        if erros:
            for erro in erros:
                flash(erro, "danger")
        else:
            registros = listar_anotacoes()
            registros.append(
                {
                    "id": gerar_id(texto[:30], {a["id"] for a in registros}),
                    "usuario_id": session["usuario"]["id"],
                    "filme_id": filme_id,
                    "parte": parte,
                    "texto": texto,
                    "criado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
                }
            )
            gravar_json(ANOTACOES_JSON, registros)
            flash("Anotação de repertório salva.", "success")
            return redirect(url_for("anotacoes"))

    return render_template(
        "anotacoes.html",
        titulo_pagina="Minhas anotações",
        anotacoes=anotacoes_do_usuario(),
        filmes=sorted(filmes, key=lambda f: f["titulo"].lower()),
        titulos={f["id"]: f["titulo"] for f in filmes},
        partes=PARTES,
    )


# --------------------------------------------------------------------------
# Rota 8 — Editar anotação (POST) — UPDATE
# --------------------------------------------------------------------------
@app.route("/anotacoes/<anotacao_id>/editar", methods=["POST"])
@login_obrigatorio
def anotacao_editar(anotacao_id):
    registros = listar_anotacoes()
    texto = (request.form.get("texto") or "").strip()
    parte = request.form.get("parte", "introducao")
    alvo = next(
        (a for a in registros if a["id"] == anotacao_id and a.get("usuario_id") == session["usuario"]["id"]),
        None,
    )
    if alvo is None:
        flash("Anotação não encontrada.", "danger")
    elif len(texto) < 15:
        flash("A anotação deve ter pelo menos 15 caracteres.", "danger")
    else:
        alvo["texto"] = texto
        alvo["parte"] = parte if parte in PARTES else alvo["parte"]
        alvo["criado_em"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        gravar_json(ANOTACOES_JSON, registros)
        flash("Anotação atualizada.", "success")
    return redirect(url_for("anotacoes"))


# --------------------------------------------------------------------------
# Rota 9 — Excluir anotação (POST) — DELETE
# --------------------------------------------------------------------------
@app.route("/anotacoes/<anotacao_id>/excluir", methods=["POST"])
@login_obrigatorio
def anotacao_excluir(anotacao_id):
    registros = listar_anotacoes()
    restantes = [
        a
        for a in registros
        if not (a["id"] == anotacao_id and a.get("usuario_id") == session["usuario"]["id"])
    ]
    gravar_json(ANOTACOES_JSON, restantes)
    flash("Anotação excluída.", "success")
    return redirect(url_for("anotacoes"))


# --------------------------------------------------------------------------
# Rota 10 — Assistente de redação (IA) — página e API (GET + POST)
# --------------------------------------------------------------------------
@app.route("/assistente")
def assistente():
    return render_template(
        "assistente.html",
        titulo_pagina="Assistente de redação",
        sugestoes=ia.PERGUNTAS_SUGERIDAS,
    )


@app.route("/api/assistente", methods=["POST"])
def api_assistente():
    dados = request.get_json(silent=True) or {}
    mensagem = dados.get("mensagem", "")
    resposta = ia.responder(mensagem, listar_filmes())
    return jsonify(resposta)


# --------------------------------------------------------------------------
# Rota 11 — Estrutura da redação (GET)
# --------------------------------------------------------------------------
@app.route("/estrutura")
def estrutura():
    filmes = listar_filmes()
    por_parte = {
        parte: sorted(
            [f for f in filmes if f.get("parte") == parte],
            key=lambda f: f.get("imdb", 0),
            reverse=True,
        )[:4]
        for parte in PARTES
    }
    return render_template("estrutura.html", titulo_pagina="Estrutura da redação", por_parte=por_parte)


# --------------------------------------------------------------------------
# Rota 12 — Acessibilidade (GET)
# --------------------------------------------------------------------------
@app.route("/acessibilidade")
def acessibilidade():
    return render_template("acessibilidade.html", titulo_pagina="Acessibilidade")


# --------------------------------------------------------------------------
# Rota 13 — Sobre o projeto (GET)
# --------------------------------------------------------------------------
@app.route("/sobre")
def sobre():
    return render_template(
        "sobre.html",
        titulo_pagina="Sobre",
        total=len(listar_filmes()),
        total_anotacoes=len(listar_anotacoes()),
        total_usuarios=len(contas.ler_usuarios()),
    )


@app.errorhandler(404)
def pagina_nao_encontrada(_erro):
    return render_template("404.html", titulo_pagina="Página não encontrada"), 404


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
