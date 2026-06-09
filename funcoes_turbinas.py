"""
funcoes_turbinas.py
-------------------
CRUD de turbinas. Cada turbina pertence a um parque (id_parque).
"""

import pandas as pd
import database as db


# ---------------- CREATE ----------------
def cadastrar_turbina():
    print("\n--- CADASTRO DE TURBINA ---")

    while True:
        tid = input("ID da turbina (ex: TURB-001): ").strip().upper()
        if tid == "":
            print("ID nao pode ser vazio.")
            continue
        if db.consultar("SELECT id FROM turbinas WHERE id = :i", {"i": tid}):
            print("ID ja cadastrado.")
            continue
        break

    id_parque = input("ID do parque vinculado: ").strip().upper()
    if not db.consultar("SELECT id FROM parques WHERE id = :i", {"i": id_parque}):
        print("Parque nao encontrado. Cadastre o parque antes.")
        return

    modelo     = input("Modelo: ").strip()
    fabricante = input("Fabricante: ").strip()

    while True:
        try:
            cap = float(input("Capacidade (MW): "))
            if cap > 0:
                break
            print("Deve ser maior que 0.")
        except ValueError:
            print("Numero valido.")

    while True:
        try:
            horas = int(input("Horas de operacao acumuladas: "))
            if horas >= 0:
                break
            print("Deve ser >= 0.")
        except ValueError:
            print("Inteiro valido.")

    db.executar("""
        INSERT INTO turbinas (id, id_parque, modelo, fabricante,
            capacidade_mw, horas_operacao, status)
        VALUES (:id, :par, :mod, :fab, :cap, :h, 'operacional')
    """, {
        "id": tid, "par": id_parque, "mod": modelo,
        "fab": fabricante, "cap": cap, "h": horas
    })
    print(f"\n[OK] Turbina '{tid}' vinculada ao parque '{id_parque}'!")


# ---------------- READ ----------------
def visualizar_turbinas():
    print("\n--- LISTA DE TURBINAS ---")
    turbinas = db.consultar("SELECT * FROM turbinas")
    if not turbinas:
        print("Nenhuma turbina cadastrada.")
        return
    for t in turbinas:
        print(f"\n  {t['id']}  ->  Parque: {t['id_parque']}")
        print(f"  Modelo/Fab.    : {t['modelo']} / {t['fabricante']}")
        print(f"  Capacidade     : {t['capacidade_mw']} MW")
        print(f"  Horas operacao : {t['horas_operacao']} h")
        print(f"  Status         : {t['status'].upper()}")


def visualizar_por_parque():
    pid = input("ID do parque: ").strip().upper()
    turbinas = db.consultar(
        "SELECT * FROM turbinas WHERE id_parque = :p", {"p": pid})
    if not turbinas:
        print(f"Nenhuma turbina para '{pid}'.")
        return
    print(f"\nTurbinas do parque '{pid}' - {len(turbinas)} encontrada(s):")
    for t in turbinas:
        print(f"  - {t['id']}  {t['modelo']}  {t['status'].upper()}  {t['capacidade_mw']} MW")


def estatisticas_turbinas():
    """Painel com Pandas: groupby por parque."""
    print("\n--- ESTATISTICAS DAS TURBINAS ---")
    turbinas = db.consultar("SELECT * FROM turbinas")
    if not turbinas:
        print("Nenhuma turbina cadastrada.")
        return

    df = pd.DataFrame(turbinas)
    total     = len(df)
    oper      = (df["status"] == "operacional").sum()
    manut     = (df["status"] == "manutencao").sum()
    inativas  = (df["status"] == "inativa").sum()
    horas_med = df["horas_operacao"].mean()

    cap_parque = df.groupby("id_parque")["capacidade_mw"].sum().round(2)
    qtd_parque = df.groupby("id_parque").size()

    print(f"\n==================================================")
    print(f"  FROTA - {total} turbina(s)")
    print(f"==================================================")
    print(f"  Operacionais    : {oper}")
    print(f"  Em manutencao   : {manut}")
    print(f"  Inativas        : {inativas}")
    print(f"  Horas medias    : {horas_med:.0f} h")
    print(f"--------------------------------------------------")
    print("  Por parque:")
    for pid in qtd_parque.index:
        print(f"    {pid}  ->  {qtd_parque[pid]} turbina(s)  |  {cap_parque[pid]} MW total")
    print(f"==================================================")


# ---------------- UPDATE ----------------
def atualizar_status():
    tid = input("ID da turbina: ").strip().upper()
    achou = db.consultar("SELECT status FROM turbinas WHERE id = :i", {"i": tid})
    if not achou:
        print("Turbina nao encontrada.")
        return
    print(f"Status atual: {achou[0]['status'].upper()}")
    print("1 - Operacional\n2 - Em manutencao\n3 - Inativa")
    try:
        opc = int(input("Novo status: "))
    except ValueError:
        print("Opcao invalida.")
        return
    mapa = {1: "operacional", 2: "manutencao", 3: "inativa"}
    if opc in mapa:
        db.executar("UPDATE turbinas SET status = :s WHERE id = :i",
                    {"s": mapa[opc], "i": tid})
        print(f"[OK] Status -> {mapa[opc].upper()}")
    else:
        print("Opcao invalida.")


def atualizar_horas():
    tid = input("ID da turbina: ").strip().upper()
    achou = db.consultar("SELECT horas_operacao FROM turbinas WHERE id = :i", {"i": tid})
    if not achou:
        print("Turbina nao encontrada.")
        return
    print(f"Horas atuais: {achou[0]['horas_operacao']} h")
    while True:
        try:
            h = int(input("Novas horas: "))
            if h >= 0:
                db.executar("UPDATE turbinas SET horas_operacao = :h WHERE id = :i",
                            {"h": h, "i": tid})
                print("[OK] Horas atualizadas!")
                return
            print("Deve ser >= 0.")
        except ValueError:
            print("Inteiro valido.")


# ---------------- DELETE ----------------
def inativar_ou_remover_turbina():
    tid = input("ID da turbina: ").strip().upper()
    achou = db.consultar("SELECT * FROM turbinas WHERE id = :i", {"i": tid})
    if not achou:
        print("Turbina nao encontrada.")
        return
    print(f"\nTurbina: {achou[0]['id']} | Status: {achou[0]['status'].upper()}")
    print("1 - Inativar (mantem historico)")
    print("2 - Remover completamente")
    print("3 - Cancelar")
    try:
        opc = int(input("Escolha: "))
    except ValueError:
        print("Opcao invalida.")
        return
    if opc == 1:
        db.executar("UPDATE turbinas SET status = 'inativa' WHERE id = :i", {"i": tid})
        print("[OK] Turbina inativada.")
    elif opc == 2:
        try:
            if int(input("Remover permanentemente? 1-Sim / 2-Nao: ")) == 1:
                db.executar("DELETE FROM turbinas WHERE id = :i", {"i": tid})
                print("[OK] Turbina removida.")
            else:
                print("Remocao cancelada.")
        except ValueError:
            print("Opcao invalida.")
    elif opc == 3:
        print("Operacao cancelada.")
    else:
        print("Opcao invalida.")
