"""
validacao.py
------------
Funcoes de validacao usadas em todo o sistema.
Mesmo estilo do arquivo original: funcoes simples com re.
"""

import re
import hashlib


def validar_email(email):
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(padrao, email))


def validar_telefone(telefone):
    tele = r'^(\d{2})\s?(9?\d{4})-?(\d{4})$'
    return bool(re.match(tele, telefone))


def gerar_hash(senha):
    """
    Transforma a senha em um 'hash' (codigo embaralhado).
    Assim a senha real nunca fica salva no banco.
    Usa o algoritmo SHA-256 da biblioteca padrao do Python.
    """
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


def conferir_senha(senha_digitada, hash_salvo):
    """
    Compara a senha digitada (gerando o hash dela) com o hash que
    esta salvo no banco. Retorna True se forem iguais.
    """
    return gerar_hash(senha_digitada) == hash_salvo
