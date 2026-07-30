"""
CineRepertório — UC31: Desenvolvimento Web com Flask
Aplicação web de repertórios socioculturais (filmes) para a redação do ENEM.

Armazenamento: arquivos JSON em /data (sem banco de dados).
Operações: CRUD completo de filmes e de anotações de repertório.
"""

import json
import os
import re
import unicodedata
from datetime import datetime

from flask import Flask, flash, redirect, render_template, request, url_for

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
FILMES_JSON = os.path.join(DATA_DIR, "filmes.json")
ANOTACOES_JSON = os.path.join(DATA_DIR, "anotacoes.json")

app = Flask(__name__)
app.secret_key = "cinerepertorio-uc31"

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


# --------------------------------------------------------------------------
# Utilidades de apresentação
# --------------------------------------------------------------------------
def lojas(titulo):
    """Links de compra/aluguel do filme nas principais lojas digitais."""
    from urllib.parse import quote_plus

    termo = quote_plus(titulo)
    return [
        {"nome": "Prime Video", "url": f"https://www.primevideo.com/search?phrase={termo}"},
        {"nome": "Apple TV", "url": f"https://tv.apple.com/search?term={termo}"},
        {"nome": "Google Play", "url": f"https://play.google.com/store/search?q={termo}&c=movies"},
    ]


def imdb_url(titulo, ano):
    from urllib.parse import quote_plus

    return f"https://www.imdb.com/find/?q={quote_plus(f'{titulo} {ano}')}"


@app.context_processor
def injetar_globais():
    """Disponibiliza funções e dados para todos os templates."""
    return {
        "lojas": lojas,
        "imdb_url": imdb_url,
        "rotulo_parte": ROTULO_PARTE,
        "ano_atual": datetime.now().year,
    }


@app.template_filter("cartaz")
def filtro_cartaz(valor):
    """Aceita URL externa ou nome de arquivo local em /static/img."""
    if not valor:
        return ""
    if valor.startswith("http"):
        return valor
    return url_for("static", filename=f"img/{valor}")


# --------------------------------------------------------------------------
# Rota 1 — Página inicial (GET)
# --------------------------------------------------------------------------
@app.route("/")
def index():
    filmes = listar_filmes()
    destaques = sorted(filmes, key=lambda f: f.get("imdb", 0), reverse=True)[:12]
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
    anotacoes = [a for a in listar_anotacoes() if a.get("filme_id") == filme_id]
    return render_template(
        "detalhe.html",
        titulo_pagina=filme["titulo"],
        filme=filme,
        relacionados=relacionados,
        anotacoes=anotacoes,
    )


# --------------------------------------------------------------------------
# Rota 4 — Cadastrar novo filme (GET + POST) — CREATE
# --------------------------------------------------------------------------
@app.route("/filmes/novo", methods=["GET", "POST"])
def filme_novo():
    if request.method == "POST":
        erros = validar_filme(request.form)
        if erros:
            for erro in erros:
                flash(erro, "danger")
            return render_template(
                "form_filme.html",
                titulo_pagina="Novo filme",
                filme=request.form,
                partes=PARTES,
                modo="novo",
            )

        filmes = listar_filmes()
        novo = montar_filme(request.form, gerar_id(request.form["titulo"], {f["id"] for f in filmes}))
        filmes.append(novo)
        gravar_json(FILMES_JSON, filmes)
        flash(f"Filme “{novo['titulo']}” cadastrado com sucesso.", "success")
        return redirect(url_for("filme_detalhe", filme_id=novo["id"]))

    return render_template(
        "form_filme.html", titulo_pagina="Novo filme", filme={}, partes=PARTES, modo="novo"
    )


# --------------------------------------------------------------------------
# Rota 5 — Editar filme (GET + POST) — UPDATE
# --------------------------------------------------------------------------
@app.route("/filmes/<filme_id>/editar", methods=["GET", "POST"])
def filme_editar(filme_id):
    filmes = listar_filmes()
    indice = next((i for i, f in enumerate(filmes) if f["id"] == filme_id), None)
    if indice is None:
        return render_template("404.html", titulo_pagina="Não encontrado"), 404

    if request.method == "POST":
        erros = validar_filme(request.form)
        if erros:
            for erro in erros:
                flash(erro, "danger")
            return render_template(
                "form_filme.html",
                titulo_pagina="Editar filme",
                filme=request.form,
                partes=PARTES,
                modo="editar",
                filme_id=filme_id,
            )
        atualizado = montar_filme(request.form, filme_id)
        atualizado["cartaz"] = request.form.get("cartaz") or filmes[indice].get("cartaz", "")
        atualizado["cor"] = filmes[indice].get("cor", "from-amber-500/30 to-slate-900/60")
        filmes[indice] = atualizado
        gravar_json(FILMES_JSON, filmes)
        flash("Filme atualizado com sucesso.", "success")
        return redirect(url_for("filme_detalhe", filme_id=filme_id))

    filme = dict(filmes[indice])
    filme["temas_texto"] = ", ".join(filme.get("temas", []))
    return render_template(
        "form_filme.html",
        titulo_pagina="Editar filme",
        filme=filme,
        partes=PARTES,
        modo="editar",
        filme_id=filme_id,
    )


# --------------------------------------------------------------------------
# Rota 6 — Excluir filme (POST) — DELETE
# --------------------------------------------------------------------------
@app.route("/filmes/<filme_id>/excluir", methods=["POST"])
def filme_excluir(filme_id):
    filmes = listar_filmes()
    restantes = [f for f in filmes if f["id"] != filme_id]
    if len(restantes) == len(filmes):
        flash("Filme não encontrado.", "danger")
    else:
        gravar_json(FILMES_JSON, restantes)
        anotacoes = [a for a in listar_anotacoes() if a.get("filme_id") != filme_id]
        gravar_json(ANOTACOES_JSON, anotacoes)
        flash("Filme excluído do catálogo.", "success")
    return redirect(url_for("filmes_lista"))


# --------------------------------------------------------------------------
# Rota 7 — Anotações de repertório: listar e criar (GET + POST)
# --------------------------------------------------------------------------
@app.route("/anotacoes", methods=["GET", "POST"])
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
                    "filme_id": filme_id,
                    "parte": parte,
                    "texto": texto,
                    "criado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
                }
            )
            gravar_json(ANOTACOES_JSON, registros)
            flash("Anotação de repertório salva.", "success")
            return redirect(url_for("anotacoes"))

    registros = listar_anotacoes()
    titulos = {f["id"]: f["titulo"] for f in filmes}
    return render_template(
        "anotacoes.html",
        titulo_pagina="Minhas anotações",
        anotacoes=registros,
        filmes=sorted(filmes, key=lambda f: f["titulo"].lower()),
        titulos=titulos,
        partes=PARTES,
    )


# --------------------------------------------------------------------------
# Rota 8 — Excluir anotação (POST)
# --------------------------------------------------------------------------
@app.route("/anotacoes/<anotacao_id>/excluir", methods=["POST"])
def anotacao_excluir(anotacao_id):
    registros = listar_anotacoes()
    restantes = [a for a in registros if a["id"] != anotacao_id]
    gravar_json(ANOTACOES_JSON, restantes)
    flash("Anotação excluída.", "success")
    return redirect(url_for("anotacoes"))


# --------------------------------------------------------------------------
# Rota 9 — Estrutura da redação (GET)
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
# Rota 10 — Sobre o projeto (GET)
# --------------------------------------------------------------------------
@app.route("/sobre")
def sobre():
    return render_template(
        "sobre.html",
        titulo_pagina="Sobre",
        total=len(listar_filmes()),
        total_anotacoes=len(listar_anotacoes()),
    )


# --------------------------------------------------------------------------
# Validação e montagem de dados
# --------------------------------------------------------------------------
def validar_filme(form):
    erros = []
    if len((form.get("titulo") or "").strip()) < 2:
        erros.append("Informe o título do filme.")
    if len((form.get("diretor") or "").strip()) < 2:
        erros.append("Informe o nome da direção.")
    try:
        ano = int(form.get("ano") or 0)
        if ano < 1895 or ano > datetime.now().year + 1:
            erros.append("Informe um ano de lançamento válido.")
    except ValueError:
        erros.append("O ano deve ser um número.")
    try:
        nota = float((form.get("imdb") or "0").replace(",", "."))
        if nota < 0 or nota > 10:
            erros.append("A nota do IMDb deve estar entre 0 e 10.")
    except ValueError:
        erros.append("A nota do IMDb deve ser um número.")
    if not (form.get("temas") or "").strip():
        erros.append("Informe pelo menos um tema.")
    if len((form.get("sinopse") or "").strip()) < 20:
        erros.append("A sinopse deve ter pelo menos 20 caracteres.")
    if len((form.get("citacao") or "").strip()) < 20:
        erros.append("Escreva a citação pronta para a redação (mínimo 20 caracteres).")
    if (form.get("parte") or "") not in PARTES:
        erros.append("Selecione o parágrafo em que o filme se encaixa.")
    return erros


def montar_filme(form, filme_id):
    return {
        "id": filme_id,
        "titulo": form["titulo"].strip(),
        "ano": int(form["ano"]),
        "diretor": form["diretor"].strip(),
        "imdb": round(float(form["imdb"].replace(",", ".")), 1),
        "temas": [t.strip() for t in form["temas"].split(",") if t.strip()],
        "sinopse": form["sinopse"].strip(),
        "comoUsar": (form.get("comoUsar") or "").strip(),
        "citacao": form["citacao"].strip(),
        "parte": form["parte"],
        "cor": "from-amber-500/30 to-slate-900/60",
        "cartaz": (form.get("cartaz") or "").strip(),
    }


@app.errorhandler(404)
def pagina_nao_encontrada(_erro):
    return render_template("404.html", titulo_pagina="Página não encontrada"), 404


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
