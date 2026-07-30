# CineRepertório

Aplicação web em **Flask** que reúne filmes utilizáveis como **repertório sociocultural**
na redação do ENEM: nota do IMDb, sinopse, tema, parágrafo ideal, citação pronta,
links para assistir e anotações pessoais do estudante.

Projeto desenvolvido para a **UC31 — Desenvolvimento Web com Flask**.

## Como executar

```bash
# 1. (opcional) criar ambiente virtual
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 2. instalar dependências
pip install -r requirements.txt

# 3. rodar
python app.py
```

Acesse: http://localhost:5000

## Estrutura do projeto

```
cinerepertorio/
├── app.py                  # rotas e regras da aplicação
├── requirements.txt
├── data/
│   ├── filmes.json         # catálogo (52 filmes) — CRUD completo
│   └── anotacoes.json      # anotações do estudante — CRUD
├── static/
│   ├── estilo.css          # tema escuro com destaque dourado
│   ├── script.js           # esteiras, copiar citação, filtros
│   └── img/                # cartaz local
└── templates/
    ├── base.html           # template-pai (herança Jinja2)
    ├── _cartaz.html        # componente reutilizável de cartaz
    ├── index.html
    ├── filmes.html
    ├── detalhe.html
    ├── form_filme.html
    ├── anotacoes.html
    ├── estrutura.html
    ├── sobre.html
    └── 404.html
```

## Rotas

| Rota | Métodos | Função |
|---|---|---|
| `/` | GET | Página inicial com esteiras automáticas de cartazes |
| `/filmes` | GET | Catálogo com busca, filtro por tema/parágrafo e ordenação (READ) |
| `/filmes/<id>` | GET | Detalhe do filme, citação pronta e lojas |
| `/filmes/novo` | GET, POST | Cadastro de filme (CREATE) |
| `/filmes/<id>/editar` | GET, POST | Edição de filme (UPDATE) |
| `/filmes/<id>/excluir` | POST | Exclusão de filme (DELETE) |
| `/anotacoes` | GET, POST | Anotações de repertório (READ e CREATE) |
| `/anotacoes/<id>/excluir` | POST | Exclusão de anotação (DELETE) |
| `/estrutura` | GET | Guia da estrutura da redação |
| `/sobre` | GET | Documentação do projeto |

## Tecnologias

Python 3, Flask, Jinja2, Bootstrap 5, CSS3, JavaScript e arquivos JSON
(sem banco de dados).

## Acessibilidade

Link "pular para o conteúdo", HTML semântico, `alt` em todas as imagens,
`label` em todos os campos, avisos com `aria-live`, foco visível, alto contraste,
animações que param no hover/foco e respeito a `prefers-reduced-motion`.
