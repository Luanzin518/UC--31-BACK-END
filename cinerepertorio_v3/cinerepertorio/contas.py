"""
CineRepertório — módulo de contas de usuário.

Responsável por cadastro, login, troca de conta e autenticação de dois
fatores (A2F) por código enviado ao e-mail. Os dados ficam em
data/usuarios.json (sem banco de dados), com a senha guardada apenas em
formato de hash PBKDF2-SHA256 + salt aleatório — a senha original nunca é
gravada em disco.
"""

import hashlib
import json
import os
import random
import re
import secrets
import unicodedata
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USUARIOS_JSON = os.path.join(BASE_DIR, "data", "usuarios.json")

# Códigos de A2F pendentes ficam apenas em memória (expiram em 10 minutos).
CODIGOS_PENDENTES = {}
VALIDADE_CODIGO = timedelta(minutes=10)

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$")


# --------------------------------------------------------------------------
# Persistência
# --------------------------------------------------------------------------
def ler_usuarios():
    if not os.path.exists(USUARIOS_JSON):
        return []
    try:
        with open(USUARIOS_JSON, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except (json.JSONDecodeError, OSError):
        return []


def gravar_usuarios(usuarios):
    os.makedirs(os.path.dirname(USUARIOS_JSON), exist_ok=True)
    with open(USUARIOS_JSON, "w", encoding="utf-8") as arquivo:
        json.dump(usuarios, arquivo, ensure_ascii=False, indent=2)


def buscar_por_email(email):
    email = (email or "").strip().lower()
    return next((u for u in ler_usuarios() if u["email"] == email), None)


# --------------------------------------------------------------------------
# Segurança da senha
# --------------------------------------------------------------------------
def criar_hash(senha, salt=None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), salt.encode("utf-8"), 120000)
    return salt, digest.hex()


def senha_confere(usuario, senha):
    _, teste = criar_hash(senha, usuario["salt"])
    return secrets.compare_digest(teste, usuario["senha_hash"])


def forca_da_senha(senha):
    """Devolve uma lista de problemas encontrados na senha."""
    problemas = []
    if len(senha) < 8:
        problemas.append("A senha deve ter no mínimo 8 caracteres.")
    if not re.search(r"[A-Za-zÀ-ÿ]", senha):
        problemas.append("A senha deve conter pelo menos uma letra.")
    if not re.search(r"\d", senha):
        problemas.append("A senha deve conter pelo menos um número.")
    return problemas


# --------------------------------------------------------------------------
# Cadastro
# --------------------------------------------------------------------------
def iniciais(nome, sobrenome):
    texto = f"{nome} {sobrenome}".strip()
    partes = [p for p in texto.split() if p]
    letras = "".join(p[0] for p in partes[:2]).upper()
    normalizado = unicodedata.normalize("NFKD", letras)
    return normalizado.encode("ascii", "ignore").decode("ascii") or "?"


def validar_cadastro(form):
    erros = []
    nome = (form.get("nome") or "").strip()
    sobrenome = (form.get("sobrenome") or "").strip()
    email = (form.get("email") or "").strip().lower()
    senha = form.get("senha") or ""
    confirmar = form.get("confirmar") or ""

    if len(nome) < 2:
        erros.append("Informe o seu nome.")
    if len(sobrenome) < 2:
        erros.append("Informe o seu sobrenome.")
    if not EMAIL_REGEX.match(email):
        erros.append("Informe um e-mail válido.")
    elif buscar_por_email(email):
        erros.append("Já existe uma conta cadastrada com este e-mail.")
    erros.extend(forca_da_senha(senha))
    if senha != confirmar:
        erros.append("As duas senhas digitadas não são iguais.")
    if (form.get("protecao") or "") not in ("a2f", "simples"):
        erros.append("Escolha o nível de proteção da conta.")
    return erros


def criar_usuario(form):
    """Cria o usuário no JSON e devolve o registro criado."""
    salt, senha_hash = criar_hash(form["senha"])
    usuario = {
        "id": secrets.token_hex(8),
        "nome": form["nome"].strip(),
        "sobrenome": form["sobrenome"].strip(),
        "email": form["email"].strip().lower(),
        "salt": salt,
        "senha_hash": senha_hash,
        "a2f": form.get("protecao") == "a2f",
        "iniciais": iniciais(form["nome"], form["sobrenome"]),
        "criado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
    }
    usuarios = ler_usuarios()
    usuarios.append(usuario)
    gravar_usuarios(usuarios)
    return usuario


def atualizar_usuario(usuario_id, campos):
    usuarios = ler_usuarios()
    for usuario in usuarios:
        if usuario["id"] == usuario_id:
            usuario.update(campos)
            gravar_usuarios(usuarios)
            return usuario
    return None


# --------------------------------------------------------------------------
# Autenticação de dois fatores (A2F)
# --------------------------------------------------------------------------
def gerar_codigo(email):
    """Gera o código de 6 dígitos e simula o envio por e-mail.

    Em produção, este ponto chamaria um serviço de SMTP. No projeto
    acadêmico o código é escrito no terminal e devolvido para a interface,
    para que a verificação possa ser testada sem servidor de e-mail.
    """
    codigo = f"{random.randint(0, 999999):06d}"
    CODIGOS_PENDENTES[email] = {"codigo": codigo, "expira": datetime.now() + VALIDADE_CODIGO}
    print(f"[A2F] Código enviado para {email}: {codigo}")
    return codigo


def validar_codigo(email, informado):
    registro = CODIGOS_PENDENTES.get(email)
    if not registro:
        return False, "Nenhum código pendente. Faça login novamente."
    if datetime.now() > registro["expira"]:
        CODIGOS_PENDENTES.pop(email, None)
        return False, "O código expirou. Solicite um novo."
    if (informado or "").strip() != registro["codigo"]:
        return False, "Código incorreto. Confira o e-mail e tente de novo."
    CODIGOS_PENDENTES.pop(email, None)
    return True, ""


def dados_publicos(usuario):
    """Versão do usuário que pode ir para a sessão/template (sem senha)."""
    return {
        "id": usuario["id"],
        "nome": usuario["nome"],
        "sobrenome": usuario["sobrenome"],
        "email": usuario["email"],
        "iniciais": usuario["iniciais"],
        "a2f": usuario["a2f"],
    }
