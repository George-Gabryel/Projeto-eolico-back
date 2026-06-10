
import re
import hashlib


def validar_email(email):
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(padrao, email))


def validar_telefone(telefone):
    tele = r'^(\d{2})\s?(9?\d{4})-?(\d{4})$'
    return bool(re.match(tele, telefone))


def gerar_hash(senha):
  
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


def conferir_senha(senha_digitada, hash_salvo):
    
    return gerar_hash(senha_digitada) == hash_salvo
