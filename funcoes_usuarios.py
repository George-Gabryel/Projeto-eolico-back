"""
funcoes_usuarios.py
-------------------
CRUD de usuarios. Mesmo estilo simples do projeto original
(funcoes soltas, loops, try/except), mas salvando no SQLite.
"""

import database as db
import validacao as validar


# ---------------- CREATE ----------------
def cadastrar_usuario():
    print("\n--- CADASTRO DE USUARIO ---")

    # E-mail (valido e ainda nao cadastrado)
    while True:
        email = input("E-mail: ").strip()
        if not validar.validar_email(email):
            print("E-mail invalido. Tente novamente.")
            continue
        existentes = db.consultar(
            "SELECT email FROM usuarios WHERE email = :e", {"e": email})
        if existentes:
            print("Este e-mail ja esta cadastrado.")
            continue
        break

    nome = input("Nome de usuario: ").strip()

    # Telefone
    while True:
        telefone = input("Telefone (ex: 81 99999-9999): ").strip()
        if validar.validar_telefone(telefone):
            break
        print("Telefone invalido. Tente novamente.")

    senha = input("Senha: ").strip()

    # Perfil
    perfis = ["Funcionario", "Cliente", "Gerente"]
    while True:
        print(f"Perfis disponiveis: {perfis}")
        perfil = input("Tipo de perfil: ").strip().lower()
        if perfil in ["funcionario", "funcionário"]:
            perfil = "Funcionario"; break
        elif perfil == "cliente":
            perfil = "Cliente"; break
        elif perfil == "gerente":
            perfil = "Gerente"; break
        else:
            print("Escolha um perfil valido.")

    db.executar("""
        INSERT INTO usuarios (email, usuario, telefone, senha, tipo_perfil)
        VALUES (:email, :usuario, :telefone, :senha, :perfil)
    """, {
        "email": email, "usuario": nome, "telefone": telefone,
        "senha": validar.gerar_hash(senha), "perfil": perfil
    })
    print(f"\n[OK] Usuario '{nome}' ({perfil}) cadastrado com sucesso!")


# ---------------- READ ----------------
def visualizar_usuarios():
    print("\n--- LISTA DE USUARIOS ---")
    usuarios = db.consultar("SELECT * FROM usuarios")
    if not usuarios:
        print("Nenhum usuario cadastrado.")
        return
    for u in usuarios:
        print(f"\n  {u['usuario']}  ({u['tipo_perfil']})")
        print(f"  E-mail   : {u['email']}")
        print(f"  Telefone : {u['telefone']}")


def listar_clientes():
    """Auxiliar: devolve a lista de e-mails que sao clientes."""
    clientes = db.consultar(
        "SELECT email, usuario FROM usuarios WHERE tipo_perfil = 'Cliente'")
    return clientes


# ---------------- UPDATE ----------------
def alterar_usuario():
    email = input("E-mail do usuario a alterar o nome: ").strip()
    achou = db.consultar(
        "SELECT usuario FROM usuarios WHERE email = :e", {"e": email})
    if not achou:
        print("E-mail nao encontrado.")
        return
    print("Nome atual:", achou[0]["usuario"])
    novo = input("Novo nome: ").strip()
    db.executar("UPDATE usuarios SET usuario = :n WHERE email = :e",
                {"n": novo, "e": email})
    print("[OK] Nome alterado!")


def alterar_telefone():
    email = input("E-mail do usuario: ").strip()
    achou = db.consultar(
        "SELECT telefone FROM usuarios WHERE email = :e", {"e": email})
    if not achou:
        print("E-mail nao encontrado.")
        return
    print("Telefone atual:", achou[0]["telefone"])
    while True:
        novo = input("Novo telefone: ").strip()
        if validar.validar_telefone(novo):
            db.executar("UPDATE usuarios SET telefone = :t WHERE email = :e",
                        {"t": novo, "e": email})
            print("[OK] Telefone alterado!")
            return
        print("Telefone invalido. Tente novamente.")


def alterar_senha():
    email = input("E-mail do usuario: ").strip()
    achou = db.consultar(
        "SELECT senha FROM usuarios WHERE email = :e", {"e": email})
    if not achou:
        print("E-mail nao encontrado.")
        return
    senha_atual = input("Senha atual: ").strip()
    if not validar.conferir_senha(senha_atual, achou[0]["senha"]):
        print("Senha atual incorreta.")
        return
    nova = input("Nova senha: ").strip()
    db.executar("UPDATE usuarios SET senha = :s WHERE email = :e",
                {"s": validar.gerar_hash(nova), "e": email})
    print("[OK] Senha alterada!")


# ---------------- DELETE ----------------
def apagar_usuario():
    email = input("E-mail do usuario a remover: ").strip()
    achou = db.consultar(
        "SELECT usuario FROM usuarios WHERE email = :e", {"e": email})
    if not achou:
        print("E-mail nao encontrado.")
        return
    print(f"Usuario encontrado: {achou[0]['usuario']}")
    print("1 - Sim\n2 - Nao")
    try:
        opc = int(input("Confirmar remocao? "))
    except ValueError:
        print("Opcao invalida.")
        return
    if opc == 1:
        db.executar("DELETE FROM usuarios WHERE email = :e", {"e": email})
        print("[OK] Usuario removido!")
    else:
        print("Remocao cancelada.")
