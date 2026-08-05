"""Testes automatizados do CineRepertório (UC31). Execute: python testes.py"""

import json
import app as aplicacao

cliente = aplicacao.app.test_client()
falhas = 0


def checar(descricao, condicao):
    global falhas
    print(("  OK  " if condicao else " FALHA ") + descricao)
    if not condicao:
        falhas += 1


print("== ROTAS PÚBLICAS ==")
for rota in ["/", "/filmes", "/filmes?tema=Educa%C3%A7%C3%A3o&ordem=ano", "/filmes/parasita",
             "/estrutura", "/assistente", "/acessibilidade", "/sobre",
             "/conta/criar", "/conta/entrar"]:
    checar(f"GET {rota} -> 200", cliente.get(rota).status_code == 200)
checar("GET /filmes/inexistente -> 404", cliente.get("/filmes/inexistente").status_code == 404)

print("\n== PROTEÇÃO DE ROTA ==")
checar("/anotacoes exige login", cliente.get("/anotacoes").status_code == 302)

print("\n== CONTA SEM A2F ==")
resposta = cliente.post("/conta/criar", data=dict(
    nome="Teste", sobrenome="UC31", email="teste.uc31@exemplo.com",
    senha="senha1234", confirmar="senha1234", protecao="simples"), follow_redirects=True)
checar("cadastro simples cria sessão", resposta.status_code == 200)
checar("/anotacoes acessível logado", cliente.get("/anotacoes").status_code == 200)

print("\n== CRUD DE ANOTAÇÕES ==")
cliente.post("/anotacoes", data=dict(filme_id="parasita", parte="introducao",
             texto="Usar Parasita para mostrar a desigualdade espacial."), follow_redirects=True)
registros = json.load(open(aplicacao.ANOTACOES_JSON, encoding="utf-8"))
criada = next((a for a in registros if "desigualdade espacial" in a["texto"]), None)
checar("CREATE grava no JSON", criada is not None)
if criada:
    cliente.post(f"/anotacoes/{criada['id']}/editar",
                 data=dict(texto="Texto atualizado pelo teste automatizado.", parte="conclusao"),
                 follow_redirects=True)
    registros = json.load(open(aplicacao.ANOTACOES_JSON, encoding="utf-8"))
    atual = next(a for a in registros if a["id"] == criada["id"])
    checar("UPDATE altera o texto", atual["texto"].startswith("Texto atualizado"))
    cliente.post(f"/anotacoes/{criada['id']}/excluir", follow_redirects=True)
    registros = json.load(open(aplicacao.ANOTACOES_JSON, encoding="utf-8"))
    checar("DELETE remove do JSON", all(a["id"] != criada["id"] for a in registros))

print("\n== ASSISTENTE DE IA ==")
dados = cliente.post("/api/assistente", json={"mensagem": "Escreva uma redação completa sobre saúde mental"}).get_json()
checar("gera redação autônoma", "Redação" in dados["blocos"][0]["titulo"])
checar("sugere videoaulas", len(dados["videos"]) == 2)
checar("sugere novas perguntas", len(dados["sugestoes"]) > 0)
correcao = cliente.post("/api/assistente", json={"mensagem": "Corrija a minha redação. " + ("A desigualdade social persiste no Brasil e afeta a educação pública. " * 15)}).get_json()
checar("corrige texto colado", "Nota estimada" in correcao["texto"])

print("\n== CONTA COM A2F ==")
outro = aplicacao.app.test_client()
outro.post("/conta/criar", data=dict(nome="Dois", sobrenome="Fatores", email="a2f.uc31@exemplo.com",
           senha="senha1234", confirmar="senha1234", protecao="a2f"))
import contas
codigo = contas.CODIGOS_PENDENTES["a2f.uc31@exemplo.com"]["codigo"]
checar("código de 6 dígitos gerado", len(codigo) == 6)
checar("código errado é rejeitado", outro.post("/conta/verificar", data={"codigo": "000000"}).status_code == 200)
checar("código correto libera acesso",
       outro.post("/conta/verificar", data={"codigo": codigo}, follow_redirects=True).status_code == 200)
checar("anotações liberadas após A2F", outro.get("/anotacoes").status_code == 200)

# limpeza dos usuários de teste
usuarios = [u for u in contas.ler_usuarios() if not u["email"].endswith("uc31@exemplo.com")]
contas.gravar_usuarios(usuarios)

print("\n" + ("Todos os testes passaram." if falhas == 0 else f"{falhas} teste(s) falharam."))
