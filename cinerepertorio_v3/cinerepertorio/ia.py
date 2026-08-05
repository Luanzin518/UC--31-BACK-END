"""
CineRepertório — assistente de redação (IA).

A IA funciona 100% offline: é um motor de regras treinado com a matriz de
correção do ENEM (5 competências). Ela sabe:

* redigir uma redação-modelo completa e autônoma sobre qualquer tema,
  usando os filmes do catálogo como repertório sociocultural;
* corrigir um texto colado pelo usuário, competência por competência;
* explicar cada parte da estrutura;
* indicar videoaulas curtas (shorts) e longas sobre o assunto perguntado;
* sugerir novas perguntas que o estudante pode fazer em seguida.
"""

import random
import re
import unicodedata
from urllib.parse import quote_plus

PERGUNTAS_SUGERIDAS = [
    "Escreva uma redação completa sobre saúde mental na juventude",
    "Corrija a minha redação (vou colar o texto)",
    "Como faço uma boa introdução?",
    "Como montar a proposta de intervenção?",
    "Quais filmes uso para o tema desigualdade social?",
    "Me mostre videoaulas sobre coesão e conectivos",
    "O que cai em cada uma das 5 competências?",
    "Me dê uma frase de repertório pronta sobre tecnologia",
]

CONECTIVOS = [
    "portanto", "todavia", "entretanto", "contudo", "ademais", "outrossim",
    "por conseguinte", "dessa forma", "nesse sentido", "além disso",
    "em primeiro lugar", "por fim", "logo", "assim", "porquanto",
]

MARCAS_INFORMAIS = [
    "né", "pra", "pro", "tipo assim", "vc", "voce", "a gente", "coisa",
    "muito legal", "daí", "aí", "ok", "beleza",
]

COMPETENCIAS = [
    ("Competência 1", "Domínio da norma culta escrita."),
    ("Competência 2", "Compreender o tema e aplicar repertório sociocultural produtivo."),
    ("Competência 3", "Selecionar e organizar argumentos em defesa de um ponto de vista."),
    ("Competência 4", "Usar mecanismos de coesão (conectivos, retomadas)."),
    ("Competência 5", "Propor intervenção com agente, ação, meio, finalidade e detalhamento."),
]


def _sem_acento(texto):
    normalizado = unicodedata.normalize("NFKD", texto or "")
    return normalizado.encode("ascii", "ignore").decode("ascii").lower()


def videos(assunto, curtos=True):
    """Monta a lista de videoaulas (curtas e longas) sobre o assunto."""
    termo = assunto.strip() or "redação ENEM"
    itens = [
        {
            "tipo": "Vídeo curto",
            "titulo": f"Resumo rápido: {termo}",
            "duracao": "até 1 min",
            "url": f"https://www.youtube.com/results?search_query={quote_plus(termo + ' redação enem shorts')}&sp=EgIYAQ%253D%253D",
        },
        {
            "tipo": "Aula longa",
            "titulo": f"Aula completa: {termo}",
            "duracao": "20 a 60 min",
            "url": f"https://www.youtube.com/results?search_query={quote_plus('aula completa ' + termo + ' redação enem')}&sp=EgIYAg%253D%253D",
        },
    ]
    return itens if curtos else itens[1:]


def _filmes_do_tema(catalogo, texto):
    alvo = _sem_acento(texto)
    escolhidos = [
        f for f in catalogo
        if any(_sem_acento(t) in alvo for t in f.get("temas", []))
    ]
    if not escolhidos:
        escolhidos = sorted(catalogo, key=lambda f: f.get("imdb", 0), reverse=True)
    return escolhidos[:3]


# --------------------------------------------------------------------------
# Redação autônoma
# --------------------------------------------------------------------------
def redigir(tema, catalogo):
    """Gera uma redação-modelo completa (4 parágrafos) sobre o tema."""
    tema = tema.strip().rstrip(".") or "os desafios sociais no Brasil"
    apoios = _filmes_do_tema(catalogo, tema)
    principal = apoios[0] if apoios else None
    secundario = apoios[1] if len(apoios) > 1 else principal

    def citar(filme):
        if not filme:
            return "a produção cinematográfica contemporânea"
        return f"o filme {filme['titulo']} ({filme['ano']}), de {filme['diretor']}"

    introducao = (
        f"O cinema costuma antecipar debates que a sociedade demora a encarar. Em {citar(principal)}, "
        f"essa lente se volta justamente para questões ligadas a {tema}. No Brasil contemporâneo, "
        f"o mesmo problema persiste e revela duas raízes centrais: a omissão histórica do poder público "
        f"e a naturalização do problema pela própria população."
    )
    desenvolvimento1 = (
        f"Em primeiro lugar, a ausência de políticas públicas contínuas agrava {tema}. "
        f"A Constituição Federal de 1988 garante direitos que, na prática, não alcançam toda a população, "
        f"o que produz um abismo entre a lei e a realidade. Assim como {citar(principal)} evidencia, "
        f"quando o Estado se ausenta, o cidadão é empurrado para soluções individuais e precárias. "
        f"Dessa forma, o problema deixa de ser exceção e passa a ser rotina."
    )
    desenvolvimento2 = (
        f"Ademais, a naturalização cultural do problema impede a mobilização coletiva. "
        f"{citar(secundario).capitalize()} mostra como o hábito de olhar para o outro sem enxergá-lo "
        f"transforma injustiça em paisagem. Nesse sentido, enquanto {tema} for tratado como assunto "
        f"secundário, a cobrança social permanecerá tímida e as mudanças, lentas."
    )
    conclusao = (
        f"Portanto, é imprescindível que o Ministério da Educação, em parceria com as secretarias estaduais, "
        f"promova campanhas educativas e projetos permanentes sobre {tema}, por meio de oficinas nas escolas "
        f"e de conteúdos audiovisuais nas redes sociais, a fim de formar cidadãos críticos e reduzir o problema. "
        f"Somente assim a realidade brasileira deixará de repetir o roteiro denunciado pelo cinema."
    )
    texto = "\n\n".join([introducao, desenvolvimento1, desenvolvimento2, conclusao])
    return texto, apoios


# --------------------------------------------------------------------------
# Correção
# --------------------------------------------------------------------------
def corrigir(texto):
    """Avalia o texto nas 5 competências e devolve nota estimada + dicas."""
    limpo = texto.strip()
    paragrafos = [p for p in re.split(r"\n\s*\n|\n", limpo) if p.strip()]
    palavras = re.findall(r"\b[\wÀ-ÿ]+\b", limpo)
    minusculo = limpo.lower()

    notas = {}
    dicas = []

    # C1 — norma culta
    informais = [m for m in MARCAS_INFORMAIS if re.search(rf"\b{re.escape(m)}\b", minusculo)]
    frases = [f for f in re.split(r"[.!?]", limpo) if f.strip()]
    sem_maiuscula = sum(1 for f in frases if f.strip()[:1].islower())
    nota_c1 = 200 - 40 * len(informais) - 20 * sem_maiuscula
    notas["Competência 1"] = max(40, min(200, nota_c1))
    if informais:
        dicas.append(f"Troque as marcas de oralidade por linguagem formal: {', '.join(informais[:4])}.")
    if sem_maiuscula:
        dicas.append("Comece todas as frases com letra maiúscula.")

    # C2 — tema e repertório
    tem_repertorio = bool(re.search(r"\(\d{4}\)|segundo|de acordo com|filme|constituição|autor", minusculo))
    nota_c2 = 200 if tem_repertorio and len(palavras) > 180 else (140 if tem_repertorio else 100)
    notas["Competência 2"] = nota_c2
    if not tem_repertorio:
        dicas.append("Insira um repertório sociocultural legitimado (filme com ano, lei, dado ou autor).")

    # C3 — argumentação
    nota_c3 = 200 if len(paragrafos) >= 4 else (140 if len(paragrafos) == 3 else 100)
    notas["Competência 3"] = nota_c3
    if len(paragrafos) < 4:
        dicas.append("Organize o texto em 4 parágrafos: introdução, dois desenvolvimentos e conclusão.")

    # C4 — coesão
    usados = [c for c in CONECTIVOS if c in minusculo]
    nota_c4 = min(200, 80 + 30 * len(usados))
    notas["Competência 4"] = nota_c4
    if len(usados) < 4:
        dicas.append("Use mais conectivos entre os parágrafos (ademais, todavia, dessa forma, portanto).")

    # C5 — proposta de intervenção
    elementos = {
        "agente": bool(re.search(r"minist|governo|escola|estado|mídia|secretaria|ong|família", minusculo)),
        "ação": bool(re.search(r"promover|criar|implementar|desenvolver|ampliar|realizar|campanha", minusculo)),
        "meio": bool(re.search(r"por meio|através de|mediante|com o uso", minusculo)),
        "finalidade": bool(re.search(r"a fim de|para que|com o objetivo|de modo a", minusculo)),
        "detalhamento": bool(re.search(r"como |tais como|por exemplo", minusculo)),
    }
    presentes = [k for k, v in elementos.items() if v]
    notas["Competência 5"] = min(200, 40 * len(presentes))
    faltando = [k for k, v in elementos.items() if not v]
    if faltando:
        dicas.append(f"Na conclusão, complete a proposta de intervenção com: {', '.join(faltando)}.")

    total = sum(notas.values())
    if len(palavras) < 120:
        dicas.append("O texto está curto: a redação do ENEM rende mais entre 25 e 30 linhas.")

    return {
        "notas": notas,
        "total": total,
        "palavras": len(palavras),
        "paragrafos": len(paragrafos),
        "dicas": dicas or ["Texto muito bem estruturado. Revise apenas a pontuação antes de entregar."],
    }


# --------------------------------------------------------------------------
# Roteador da conversa
# --------------------------------------------------------------------------
def responder(mensagem, catalogo):
    """Recebe a pergunta do usuário e devolve a resposta estruturada."""
    pergunta = (mensagem or "").strip()
    chave = _sem_acento(pergunta)
    resposta = {"texto": "", "blocos": [], "videos": [], "sugestoes": [], "filmes": []}

    if not pergunta:
        resposta["texto"] = "Digite a sua dúvida ou peça uma redação completa sobre um tema."
        resposta["sugestoes"] = random.sample(PERGUNTAS_SUGERIDAS, 4)
        return resposta

    # 1) Correção: texto longo ou pedido explícito
    palavras = re.findall(r"\b[\wÀ-ÿ]+\b", pergunta)
    pede_correcao = any(t in chave for t in ["corrig", "avalia", "que nota", "revis"])
    if len(palavras) > 90 or (pede_correcao and len(palavras) > 40):
        analise = corrigir(pergunta)
        resposta["texto"] = (
            f"Corrigi o seu texto pela matriz do ENEM. Nota estimada: "
            f"{analise['total']} de 1000 ({analise['palavras']} palavras, {analise['paragrafos']} parágrafos)."
        )
        resposta["blocos"] = [
            {"titulo": comp, "texto": f"{nota}/200"} for comp, nota in analise["notas"].items()
        ] + [{"titulo": "Como subir a nota", "texto": " • " + "\n • ".join(analise["dicas"])}]
        resposta["videos"] = videos("competências da redação do ENEM")
        resposta["sugestoes"] = [
            "Reescreva a minha conclusão com proposta de intervenção completa",
            "Como faço uma boa introdução?",
            "Me mostre videoaulas sobre coesão e conectivos",
        ]
        return resposta

    if pede_correcao:
        resposta["texto"] = "Cole aqui a sua redação inteira (ou grave por voz) que eu corrijo competência por competência."
        resposta["sugestoes"] = random.sample(PERGUNTAS_SUGERIDAS, 3)
        return resposta

    # 2) Redação autônoma
    if any(t in chave for t in ["escreva", "faca uma redacao", "faça uma redacao", "redacao completa", "modelo de redacao", "crie uma redacao"]):
        tema = re.sub(r".*(sobre|a respeito de)\s+", "", pergunta, flags=re.IGNORECASE).strip()
        texto, apoios = redigir(tema, catalogo)
        resposta["texto"] = f"Redação-modelo completa sobre {tema or 'o tema pedido'}:"
        resposta["blocos"] = [{"titulo": "Redação (4 parágrafos)", "texto": texto}]
        resposta["filmes"] = [
            {"titulo": f["titulo"], "ano": f["ano"], "id": f["id"], "imdb": f["imdb"]} for f in apoios
        ]
        resposta["videos"] = videos(tema or "redação nota 1000")
        resposta["sugestoes"] = [
            "Corrija esta redação para mim",
            "Troque o repertório por outro filme",
            f"Quais filmes uso para o tema {tema[:30] or 'meio ambiente'}?",
        ]
        return resposta

    # 3) Filmes por tema
    if any(t in chave for t in ["filme", "repertorio", "cartaz"]):
        apoios = _filmes_do_tema(catalogo, pergunta)
        resposta["texto"] = "Estes filmes do catálogo se encaixam melhor no que você pediu:"
        resposta["filmes"] = [
            {"titulo": f["titulo"], "ano": f["ano"], "id": f["id"], "imdb": f["imdb"]} for f in apoios
        ]
        resposta["blocos"] = [
            {"titulo": f"Citação pronta — {f['titulo']}", "texto": f.get("citacao", "")} for f in apoios
        ]
        resposta["videos"] = videos("repertório sociocultural redação ENEM")
        resposta["sugestoes"] = [
            "Escreva uma redação completa com esse repertório",
            "Como encaixo o filme na introdução?",
        ]
        return resposta

    # 4) Partes da estrutura
    partes = {
        "introducao": (
            "Introdução (4 a 5 linhas)",
            "Fórmula: repertório (filme, lei ou dado) + contextualização do tema + tese com os dois "
            "argumentos que você vai desenvolver. Nunca faça pergunta e nunca use 'eu acho'.",
        ),
        "desenvolvimento": (
            "Desenvolvimento (6 a 8 linhas cada)",
            "Fórmula: conectivo + tópico frasal (o argumento em uma frase) + repertório + explicação + "
            "consequência social + fecho que retoma a tese.",
        ),
        "conclusao": (
            "Conclusão (5 a 7 linhas)",
            "Proposta de intervenção com os 5 elementos: agente + ação + meio + finalidade + detalhamento. "
            "Ex.: 'O Ministério da Educação (agente) deve promover oficinas (ação) por meio de parcerias com "
            "escolas (meio), a fim de formar cidadãos críticos (finalidade), como projetos mensais de cinema "
            "e debate (detalhamento).'",
        ),
        "conectivo": (
            "Coesão e conectivos",
            "Introduzir: em primeiro lugar, inicialmente. Somar: ademais, outrossim, além disso. "
            "Contrapor: todavia, entretanto, em contrapartida. Concluir: portanto, dessa forma, por conseguinte.",
        ),
        "competencia": (
            "As 5 competências",
            "\n".join(f"{nome}: {desc}" for nome, desc in COMPETENCIAS),
        ),
        "tese": (
            "Tese",
            "A tese é a sua resposta ao tema em uma frase, com os dois argumentos anunciados. "
            "Ela fecha a introdução e é retomada na conclusão.",
        ),
    }
    for chave_parte, (titulo, conteudo) in partes.items():
        if chave_parte in chave or (chave_parte == "introducao" and "comec" in chave):
            resposta["texto"] = f"Sobre {titulo.lower()}:"
            resposta["blocos"] = [{"titulo": titulo, "texto": conteudo}]
            resposta["videos"] = videos(titulo)
            resposta["sugestoes"] = random.sample(PERGUNTAS_SUGERIDAS, 3)
            return resposta

    # 5) Videoaulas
    if any(t in chave for t in ["video", "aula", "youtube"]):
        assunto = re.sub(r".*(sobre|de)\s+", "", pergunta, flags=re.IGNORECASE).strip()
        resposta["texto"] = f"Separei uma versão curta e uma aula longa sobre {assunto or 'redação do ENEM'}:"
        resposta["videos"] = videos(assunto or "redação do ENEM")
        resposta["sugestoes"] = random.sample(PERGUNTAS_SUGERIDAS, 3)
        return resposta

    # 6) Resposta geral
    resposta["texto"] = (
        "Posso escrever uma redação completa sobre qualquer tema, corrigir a sua pelas 5 competências, "
        "sugerir filmes do catálogo como repertório e indicar videoaulas curtas ou longas. "
        "Me diga o tema ou cole o seu texto."
    )
    resposta["blocos"] = [{"titulo": titulo, "texto": desc} for titulo, desc in COMPETENCIAS]
    resposta["videos"] = videos(pergunta)
    resposta["sugestoes"] = random.sample(PERGUNTAS_SUGERIDAS, 4)
    return resposta
