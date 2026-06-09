"""
funcoes_drones.py
-----------------
CRUD de drones. Cada drone pertence a um parque (id_parque).
"""

import pandas as pd
import database as db


# ---------------- CREATE ----------------
def cadastrar_drone():
    print("\n--- CADASTRO DE DRONE ---")

    while True:
        did = input("ID do drone (ex: DRONE-001): ").strip().upper()
        if did == "":
            print("ID nao pode ser vazio.")
            continue
        if db.consultar("SELECT id FROM drones WHERE id = :i", {"i": did}):
            print("ID ja cadastrado.")
            continue
        break

    id_parque = input("ID do parque vinculado: ").strip().upper()
    if not db.consultar("SELECT id FROM parques WHERE id = :i", {"i": id_parque}):
        print("Parque nao encontrado. Cadastre o parque antes.")
        return

    nome = input("Nome/modelo do drone: ").strip()

    while True:
        try:
            bateria = int(input("Nivel de bateria LiPo (0-100%): "))
            if 0 <= bateria <= 100:
                break
            print("Informe entre 0 e 100.")
        except ValueError:
            print("Inteiro valido.")

    while True:
        try:
            limite = int(input("Limite maximo de voo (metros): "))
            if limite > 0:
                break
            print("Deve ser maior que 0.")
        except ValueError:
            print("Inteiro valido.")

    db.executar("""
        INSERT INTO drones (id, id_parque, nome, bateria_lipo, limite_voo, status)
        VALUES (:id, :par, :nome, :bat, :lim, 'ativo')
    """, {
        "id": did, "par": id_parque, "nome": nome,
        "bat": bateria, "lim": limite
    })
    print(f"\n[OK] Drone '{did} - {nome}' vinculado ao parque '{id_parque}'!")


# ---------------- READ ----------------
def visualizar_drones():
    print("\n--- LISTA DE DRONES ---")
    drones = db.consultar("SELECT * FROM drones")
    if not drones:
        print("Nenhum drone cadastrado.")
        return
    for d in drones:
        tag = "[APOSENTADO]" if d["status"] == "aposentado" else "[ATIVO]"
        print(f"\n{tag} {d['id']} - {d['nome']}")
        print(f"  Parque        : {d['id_parque']}")
        print(f"  Bateria LiPo  : {d['bateria_lipo']}%")
        print(f"  Limite de voo : {d['limite_voo']} m")


def estatisticas_drones():
    """Painel com Pandas."""
    print("\n--- ESTATISTICAS DOS DRONES ---")
    drones = db.consultar("SELECT * FROM drones")
    if not drones:
        print("Nenhum drone cadastrado.")
        return

    df = pd.DataFrame(drones)
    ativos    = (df["status"] == "ativo").sum()
    apos      = (df["status"] == "aposentado").sum()
    bat_media = df["bateria_lipo"].mean()
    criticos  = (df["bateria_lipo"] < 20).sum()

    print(f"\n==================================================")
    print(f"  FROTA - {len(df)} drone(s)")
    print(f"==================================================")
    print(f"  Ativos          : {ativos}")
    print(f"  Aposentados     : {apos}")
    print(f"  Bateria media   : {bat_media:.1f}%")
    print(f"  Bateria critica : {criticos} drone(s) abaixo de 20%")
    print(f"==================================================")


# ---------------- UPDATE ----------------
def atualizar_bateria():
    did = input("ID do drone: ").strip().upper()
    achou = db.consultar("SELECT bateria_lipo FROM drones WHERE id = :i", {"i": did})
    if not achou:
        print("Drone nao encontrado.")
        return
    print(f"Bateria atual: {achou[0]['bateria_lipo']}%")
    while True:
        try:
            bat = int(input("Novo nivel de bateria (0-100): "))
            if 0 <= bat <= 100:
                db.executar("UPDATE drones SET bateria_lipo = :b WHERE id = :i",
                            {"b": bat, "i": did})
                print("[OK] Bateria atualizada!")
                return
            print("Informe entre 0 e 100.")
        except ValueError:
            print("Inteiro valido.")


def alterar_limite_voo():
    did = input("ID do drone: ").strip().upper()
    achou = db.consultar("SELECT limite_voo FROM drones WHERE id = :i", {"i": did})
    if not achou:
        print("Drone nao encontrado.")
        return
    print(f"Limite atual: {achou[0]['limite_voo']} m")
    while True:
        try:
            novo = int(input("Novo limite (metros): "))
            if novo > 0:
                db.executar("UPDATE drones SET limite_voo = :l WHERE id = :i",
                            {"l": novo, "i": did})
                print("[OK] Limite atualizado!")
                return
            print("Deve ser maior que 0.")
        except ValueError:
            print("Inteiro valido.")


# ---------------- DELETE ----------------
def aposentar_ou_remover_drone():
    did = input("ID do drone: ").strip().upper()
    achou = db.consultar("SELECT * FROM drones WHERE id = :i", {"i": did})
    if not achou:
        print("Drone nao encontrado.")
        return
    print(f"\nDrone: {achou[0]['id']} - {achou[0]['nome']}")
    print("1 - Aposentar (mantem historico)")
    print("2 - Remover completamente")
    print("3 - Cancelar")
    try:
        opc = int(input("Escolha: "))
    except ValueError:
        print("Opcao invalida.")
        return
    if opc == 1:
        db.executar("UPDATE drones SET status = 'aposentado' WHERE id = :i", {"i": did})
        print("[OK] Drone aposentado.")
    elif opc == 2:
        try:
            if int(input("Remover permanentemente? 1-Sim / 2-Nao: ")) == 1:
                db.executar("DELETE FROM drones WHERE id = :i", {"i": did})
                print("[OK] Drone removido.")
            else:
                print("Remocao cancelada.")
        except ValueError:
            print("Opcao invalida.")
    elif opc == 3:
        print("Operacao cancelada.")
    else:
        print("Opcao invalida.")
