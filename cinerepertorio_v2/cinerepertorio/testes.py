"""Testes automatizados das rotas do CineRepertório (UC31)."""
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import app as aplicacao  # noqa: E402

BKP = "/tmp/bkp_cine"
os.makedirs(BKP, exist_ok=True)
shutil.copy(aplicacao.FILMES_JSON, f"{BKP}/filmes.json")
shutil.copy(aplicacao.ANOTACOES_JSON, f"{BKP}/anotacoes.json")

cliente = aplicacao.app.test_client()
falhas = []


def checar(rotulo, condicao):
    print(("  OK  " if condicao else " FALHA ") + rotulo)
    if not condicao:
        falhas.append(rotulo)


print("\n== GET ==")
for rota in ["/", "/filmes", "/filmes?tema=Educa%C3%A7%C3%A3o&ordem=ano",
             "/filmes/parasita", "/filmes/novo", "/filmes/parasita/editar",
             "/anotacoes", "/estrutura", "/sobre"]:
    r = cliente.get(rota)
    checar(f"GET {rota} -> {r.status_code}", r.status_code == 200)

checar("GET /filmes/inexistente -> 404", cliente.get("/filmes/inexistente").status_code == 404)

print("\n== CREATE ==")
r = cliente.post("/filmes/novo", data={
    "titulo": "Filme de Teste UC31", "ano": "2024", "diretor": "Equipe de Testes",
    "imdb": "8.2", "temas": "Educação, Tecnologia",
    "sinopse": "Filme criado automaticamente para validar o cadastro do sistema.",
    "comoUsar": "Usado apenas em teste automatizado.",
    "citacao": "Filme de Teste UC31 (2024) comprova que o cadastro funciona corretamente.",
    "parte": "desenvolvimento", "cartaz": "",
}, follow_redirects=True)
dados = json.load(open(aplicacao.FILMES_JSON, encoding="utf-8"))
novo = next((f for f in dados if f["id"] == "filme-de-teste-uc31"), None)
checar("POST /filmes/novo cria registro no JSON", novo is not None)

print("\n== VALIDAÇÃO ==")
antes = len(json.load(open(aplicacao.FILMES_JSON, encoding="utf-8")))
cliente.post("/filmes/novo", data={"titulo": "", "ano": "abc", "diretor": "",
                                   "imdb": "99", "temas": "", "sinopse": "curta",
                                   "citacao": "curta", "parte": "x"})
depois = len(json.load(open(aplicacao.FILMES_JSON, encoding="utf-8")))
checar("POST inválido é rejeitado", antes == depois)

print("\n== UPDATE ==")
cliente.post("/filmes/filme-de-teste-uc31/editar", data={
    "titulo": "Filme de Teste UC31", "ano": "2025", "diretor": "Equipe de Testes",
    "imdb": "9.0", "temas": "Educação", "sinopse": "Sinopse atualizada pelo teste automatizado.",
    "comoUsar": "", "citacao": "Citação atualizada pelo teste automatizado do sistema.",
    "parte": "conclusao", "cartaz": "",
}, follow_redirects=True)
dados = json.load(open(aplicacao.FILMES_JSON, encoding="utf-8"))
alvo = next(f for f in dados if f["id"] == "filme-de-teste-uc31")
checar("POST editar atualiza ano e nota", alvo["ano"] == 2025 and alvo["imdb"] == 9.0)

print("\n== ANOTAÇÕES ==")
cliente.post("/anotacoes", data={"filme_id": "parasita", "parte": "introducao",
                                 "texto": "Usar Parasita para falar de desigualdade espacial."},
             follow_redirects=True)
anots = json.load(open(aplicacao.ANOTACOES_JSON, encoding="utf-8"))
checar("POST /anotacoes cria anotação", len(anots) == 1)
if anots:
    cliente.post(f"/anotacoes/{anots[0]['id']}/excluir", follow_redirects=True)
    checar("POST excluir anotação", json.load(open(aplicacao.ANOTACOES_JSON, encoding="utf-8")) == [])

print("\n== DELETE ==")
cliente.post("/filmes/filme-de-teste-uc31/excluir", follow_redirects=True)
dados = json.load(open(aplicacao.FILMES_JSON, encoding="utf-8"))
checar("POST excluir remove filme", all(f["id"] != "filme-de-teste-uc31" for f in dados))
checar("Catálogo original preservado (52 filmes)", len(dados) == 52)

print("\n== HERANÇA DE TEMPLATES / ACESSIBILIDADE ==")
html = cliente.get("/filmes").get_data(as_text=True)
checar("base.html aplicado (navbar em todas as páginas)", "Cine" in html and "navbar" in html)
checar("link de pular conteúdo presente", "pular-conteudo" in html)
checar("Bootstrap carregado", "bootstrap@5" in html)

# restaura o estado original dos arquivos JSON
shutil.copy(f"{BKP}/filmes.json", aplicacao.FILMES_JSON)
shutil.copy(f"{BKP}/anotacoes.json", aplicacao.ANOTACOES_JSON)

print("\n" + ("TODOS OS TESTES PASSARAM" if not falhas else f"FALHAS: {falhas}"))
sys.exit(1 if falhas else 0)
