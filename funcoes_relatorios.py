"""
funcoes_relatorios.py
---------------------
CRUD de relatorios / dashboards. Cada relatorio esta ligado a um parque.
O cliente so enxerga relatorios do proprio parque.
"""

import pandas as pd
import database as db


def calcular_economia(downtime_h, capacidade_mw, custo_kwh):
    """horas x MW x 1000 kW/MW x R$/kWh -> economia estimada."""
    kwh = downtime_h * capacidade_mw * 1000
    return round(kwh * custo_kwh, 2)


# ---------------- CREATE ----------------
def criar_relatorio():
    print("\n--- CRIAR RELATORIO / DASHBOARD ---")

    while True:
        rid = input("ID do relatorio (ex: REL-001): ").strip().upper()
        if rid == "":
            print("ID nao pode ser vazio.")
            continue
        if db.consultar("SELECT id FROM relatorios WHERE id = :i", {"i": rid}):
            print("ID ja cadastrado.")
            continue
        break

    id_parque = input("ID do parque: ").strip().upper()
    parque = db.consultar(
        "SELECT capacidade_total_mw FROM parques WHERE id = :i", {"i": id_parque})
    if not parque:
        print("Parque nao encontrado.")
        return

    nome = input("Nome do relatorio: ").strip()
    print("Tipo: 1-Preditivo  2-Financeiro")
    while True:
        t = input("Escolha: ").strip()
        if t == "1":
            tipo = "preditivo"; break
        elif t == "2":
            tipo = "financeiro"; break
        print("Escolha 1 ou 2.")

    while True:
        try:
            num_oc = int(input("Nº de ocorrencias no periodo: "))
            if num_oc >= 0:
                break
            print("Deve ser >= 0.")
        except ValueError:
            print("Inteiro valido.")

    while True:
        try:
            ef = float(input("Eficacia media das dispersoes (0-100%): "))
            if 0 <= ef <= 100:
                break
            print("Entre 0 e 100.")
        except ValueError:
            print("Numero valido.")

    while True:
        try:
            dt = float(input("Horas de downtime evitadas: "))
            if dt >= 0:
                break
            print("Deve ser >= 0.")
        except ValueError:
            print("Numero valido.")

    while True:
        try:
            custo = float(input("Custo medio do kWh (R$): "))
            if custo > 0:
                break
            print("Deve ser > 0.")
        except ValueError:
            print("Numero valido.")

    economia = calcular_economia(dt, parque[0]["capacidade_total_mw"], custo)

    db.executar("""
        INSERT INTO relatorios (id, id_parque, nome, tipo,
            num_ocorrencias, eficacia_media, economia_estimada, status)
        VALUES (:id, :par, :nome, :tipo, :noc, :ef, :ec, 'ativo')
    """, {
        "id": rid, "par": id_parque, "nome": nome, "tipo": tipo,
        "noc": num_oc, "ef": ef, "ec": economia
    })
    print(f"\n[OK] Relatorio '{rid} - {nome}' criado!")
    print(f"  Economia estimada: R$ {economia:,.2f}")


# ---------------- READ ----------------
def visualizar_relatorios(email_cliente=None):
    """
    Se email_cliente for informado, mostra apenas relatorios dos parques
    daquele cliente.
    """
    print("\n--- LISTA DE RELATORIOS ---")
    if email_cliente:
        relatorios = db.consultar("""
            SELECT r.* FROM relatorios r
            JOIN parques p ON r.id_parque = p.id
            WHERE p.email_cliente = :c
        """, {"c": email_cliente})
    else:
        relatorios = db.consultar("SELECT * FROM relatorios")

    if not relatorios:
        print("Nenhum relatorio encontrado.")
        return

    for r in relatorios:
        tag = "[ARQUIVADO]" if r["status"] == "arquivado" else "[ATIVO]"
        print(f"\n{tag} {r['id']} - {r['nome']}")
        print(f"  Tipo           : {r['tipo'].upper()}")
        print(f"  Parque         : {r['id_parque']}")
        print(f"  Ocorrencias    : {r['num_ocorrencias']}")
        print(f"  Eficacia media : {r['eficacia_media']}%")
        print(f"  Economia est.  : R$ {r['economia_estimada']:,.2f}")


def visao_geral_financeira():
    """Painel com Pandas: totais, medias e groupby por tipo/parque."""
    print("\n--- VISAO GERAL FINANCEIRA ---")
    relatorios = db.consultar("SELECT * FROM relatorios")
    if not relatorios:
        print("Nenhum relatorio cadastrado.")
        return

    df = pd.DataFrame(relatorios)
    ec_total  = df["economia_estimada"].sum()
    ec_media  = df["economia_estimada"].mean()
    ef_media  = df["eficacia_media"].mean()
    por_tipo  = df.groupby("tipo")["economia_estimada"].agg(["sum", "count"])
    por_parque = df.groupby("id_parque")["economia_estimada"].sum().sort_values(ascending=False)

    print(f"\n==================================================")
    print(f"  VISAO GERAL - {len(df)} relatorio(s)")
    print(f"==================================================")
    print(f"  Economia total : R$ {ec_total:,.2f}")
    print(f"  Economia media : R$ {ec_media:,.2f}")
    print(f"  Eficacia media : {ef_media:.1f}%")
    print(f"--------------------------------------------------")
    print("  Por tipo:")
    for tipo, linha in por_tipo.iterrows():
        print(f"    {tipo.upper():<12}  {int(linha['count'])} relatorio(s)  "
              f"Total: R$ {linha['sum']:,.2f}")
    print(f"--------------------------------------------------")
    print("  Economia por parque:")
    for pid, ec in por_parque.items():
        print(f"    {pid:<12}: R$ {ec:,.2f}")
    print(f"==================================================")


# ---------------- UPDATE ----------------
def atualizar_relatorio():
    rid = input("ID do relatorio: ").strip().upper()
    achou = db.consultar("SELECT * FROM relatorios WHERE id = :i", {"i": rid})
    if not achou:
        print("Relatorio nao encontrado.")
        return
    print(f"\nRelatorio: {achou[0]['id']} - {achou[0]['nome']}")
    print("1 - Nome\n2 - Eficacia media\n3 - Nº ocorrencias")
    try:
        opc = int(input("Escolha: "))
    except ValueError:
        print("Opcao invalida.")
        return
    if opc == 1:
        novo = input("Novo nome: ").strip()
        db.executar("UPDATE relatorios SET nome = :n WHERE id = :i",
                    {"n": novo, "i": rid})
        print("[OK] Nome atualizado!")
    elif opc == 2:
        while True:
            try:
                e = float(input("Nova eficacia (0-100): "))
                if 0 <= e <= 100:
                    db.executar("UPDATE relatorios SET eficacia_media = :e WHERE id = :i",
                                {"e": e, "i": rid})
                    print("[OK] Eficacia atualizada!")
                    return
                print("Entre 0 e 100.")
            except ValueError:
                print("Numero valido.")
    elif opc == 3:
        while True:
            try:
                n = int(input("Novo nº de ocorrencias: "))
                if n >= 0:
                    db.executar("UPDATE relatorios SET num_ocorrencias = :n WHERE id = :i",
                                {"n": n, "i": rid})
                    print("[OK] Atualizado!")
                    return
                print("Deve ser >= 0.")
            except ValueError:
                print("Inteiro valido.")
    else:
        print("Opcao invalida.")


# ---------------- DELETE ----------------
def arquivar_ou_excluir_relatorio():
    rid = input("ID do relatorio: ").strip().upper()
    achou = db.consultar("SELECT * FROM relatorios WHERE id = :i", {"i": rid})
    if not achou:
        print("Relatorio nao encontrado.")
        return
    print(f"\nRelatorio: {achou[0]['id']} - {achou[0]['nome']}")
    print("1 - Arquivar (mantem historico)")
    print("2 - Excluir permanentemente")
    print("3 - Cancelar")
    try:
        opc = int(input("Escolha: "))
    except ValueError:
        print("Opcao invalida.")
        return
    if opc == 1:
        db.executar("UPDATE relatorios SET status = 'arquivado' WHERE id = :i", {"i": rid})
        print("[OK] Relatorio arquivado.")
    elif opc == 2:
        try:
            if int(input("Excluir permanentemente? 1-Sim / 2-Nao: ")) == 1:
                db.executar("DELETE FROM relatorios WHERE id = :i", {"i": rid})
                print("[OK] Relatorio excluido.")
            else:
                print("Cancelado.")
        except ValueError:
            print("Opcao invalida.")
    elif opc == 3:
        print("Operacao cancelada.")
    else:
        print("Opcao invalida.")
