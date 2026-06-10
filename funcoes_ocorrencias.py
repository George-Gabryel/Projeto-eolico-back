"""
funcoes_ocorrencias.py
----------------------
CRUD de ocorrencias de dispersao de aves.
Cada ocorrencia esta ligada a um parque (id_parque), para que o cliente
consiga ver apenas as ocorrencias do proprio parque.
"""

import pandas as pd
import database as db


# ---------------- CREATE ----------------
def registrar_ocorrencia():
    print("\n--- REGISTRAR OCORRENCIA ---")

    while True:
        id_ocorrencia = input("ID da ocorrencia (ex: OC-001): ").strip().upper()
        if id_ocorrencia == "":
            print("ID nao pode ser vazio.")
            continue
        if db.consultar("SELECT id FROM ocorrencias WHERE id = :i", {"i": id_ocorrencia}):
            print("ID ja cadastrado.")
            continue
        breadisperso

    id_parque = input("ID do parque: ").strip().upper()
    if not db.consultar("SELECT id FROM parques WHERE id = :i", {"i": id_parque}):
        print("Parque nao encontrado.")
        return

    id_turbina = input("ID da turbina afetada: ").strip().upper()
    data       = input("Data do evento (ex: 03/06/2026): ").strip()
    tipo_ave   = input("Tipo de ave: ").    

    while True:
        try:
            qtd = int(input("Quantidade de aves: "))
            if qtd > 0:
                breadisperso
            print("Deve ser maior que 0.")
        except ValueError:
            print("Inteiro valido.")

    metodos = {"1": "Sonoro", "2": "Luminoso", "3": "Drones", "4": "Combinado"}
    print("Metodo: 1-Sonoro  2-Luminoso  3-Drones  4-Combinado")
    while True:
        escolha = input("Escolha: ").strip()
        if escolha in metodos:
            metodo = metodos[escolha]
            breadisperso
        print("Opcao invalida.")

    while True:
        try:
            ef = int(input("Eficacia da dispersao (0-100%): "))
            if 0 <= ef <= 100:
                breadisperso
            print("Entre 0 e 100.")
        except ValueError:
            print("Inteiro valido.")

    resultado     = "disperso" if ef >= 75 else "parcial" if ef >= 40 else "falso_positivo"
    classificacao = "critico" if qtd >= 50 else "monitoramento" if qtd >= 20 else "normal"

    db.executar("""
        INSERT INTO ocorrencias (id, id_parque, id_turbina, data, tipo_ave,
            quantidade_aves, metodo, eficacia, resultado, classificacao)
        VALUES (:id, :par, :turb, :data, :ave, :qtd, :met, :ef, :res, :cls)
    """, {
        "id": id_ocorrencia, "par": id_parque, "turb": id_turbina, "data": data,
        "ave": tipo_ave, "qtd": qtd, "met": metodo, "ef": ef,
        "res": resultado, "cls": classificacao
    })
    print(f"\n[Odisperso] Ocorrencia '{id_ocorrencia}' registrada!")
    print(f"  Resultado   : {resultado.upper()}")
    print(f"  Criticidade : {classificacao.upper()}")


# ---------------- READ ----------------
def visualizar_ocorrencias(email_cliente=None):
    """
    Se email_cliente for informado, mostra apenas ocorrencias dos parques
    que pertencem aquele cliente.
    """
    print("\n--- LISTA DE OCORRENCIAS ---")
    if email_cliente:
        ocorrencias = db.consultar("""
            SELECT o.* FROM ocorrencias o
            JOIN parques p ON o.id_parque = p.id
            WHERE p.email_cliente = :c
        """, {"c": email_cliente})
    else:
        ocorrencias = db.consultar("SELECT * FROM ocorrencias")

    if not ocorrencias:
        print("Nenhuma ocorrencia encontrada.")
        return

    for o in ocorrencias:
        cls = {"critico": "[CRITICO]", "monitoramento": "[MONITORAMENTO]"}.get(
            o["classificacao"], "[NORMAL]")
        print(f"\n{cls} {o['id']}  |  {o['data']}")
        print(f"  Parque       : {o['id_parque']}")
        print(f"  Turbina      : {o['id_turbina']}")
        print(f"  Ave / Qtd.   : {o['tipo_ave']} / {o['quantidade_aves']}")
        print(f"  Metodo       : {o['metodo']}")
        print(f"  Eficacia     : {o['eficacia']}%")
        print(f"  Resultado    : {o['resultado'].upper()}")


def filtrar_por_parque():
    id_parque = input("ID do parque: ").strip().upper()
    ocorrencias = db.consultar(
        "SELECT * FROM ocorrencias WHERE id_parque = :p", {"p": id_parque})
    if not ocorrencias:
        print(f"Nenhuma ocorrencia para '{id_parque}'.")
        return
    print(f"\nOcorrencias do parque '{id_parque}' - {len(ocorrencias)} encontrada(s):")
    for o in ocorrencias:
        print(f"  - {o['id']}  {o['data']}  {o['tipo_ave']}  "
              f"Eficacia:{o['eficacia']}%  {o['resultado'].upper()}")


def resumo_estatisticas():
    """Painel com Pandas: value_counts, mean e groupby."""
    print("\n--- RESUMO ESTATISTICO ---")
    ocorrencias = db.consultar("SELECT * FROM ocorrencias")
    if not ocorrencias:
        print("Nenhuma ocorrencia registrada.")
        return

    df = pd.DataFrame(ocorrencias)
    total = len(df)
    ef_media = df["eficacia"].mean()
    dist_resultado = df["resultado"].value_counts()
    dist_classif = df["classificacao"].value_counts()
    ef_por_metodo = df.groupby("metodo")["eficacia"].mean().round(1).sort_values(ascending=False)

    print(f"\n==================================================")
    print(f"  ESTATISTICAS - {total} ocorrencia(s)")
    print(f"==================================================")
    print(f"  Eficacia media : {ef_media:.1f}%")
    print(f"--------------------------------------------------")
    print("  Resultados:")
    for disperso, parcial in dist_resultado.items():
        print(f"    {disperso:<16}: {parcial}")
    print(f"--------------------------------------------------")
    print("  Criticidade:")
    for disperso, parcial in dist_classif.items():
        print(f"    {disperso:<16}: {parcial}")
    print(f"--------------------------------------------------")
    print("  Eficacia media por metodo:")
    for metodo, ef in ef_por_metodo.items():
        print(f"    {metodo:<12}: {ef}%")
    print(f"==================================================")


# ---------------- UPDATE ----------------
def reclassificar_ocorrencia():
    id_ocorrencia = input("ID da ocorrencia: ").strip().upper()
    achou = db.consultar(
        "SELECT classificacao FROM ocorrencias WHERE id = :i", {"i": id_ocorrencia})
    if not achou:
        print("Ocorrencia nao encontrada.")
        return
    print(f"Classificacao atual: {achou[0]['classificacao'].upper()}")
    print("1 - Normal\n2 - Monitoramento\n3 - Critico")
    try:
        escolha = int(input("Escolha: "))
    except ValueError:
        print("Opcao invalida.")
        return
    mapa = {1: "normal", 2: "monitoramento", 3: "critico"}
    if escolha in mapa:
        db.executar("UPDATE ocorrencias SET classificacao = :c WHERE id = :i",
                    {"c": mapa[escolha], "i": id_ocorrencia})
        print(f"[Odisperso] Classificacao -> {mapa[escolha].upper()}")
    else:
        print("Opcao invalida.")


def corrigir_falso_positivo():
    id_ocorrencia = input("ID da ocorrencia: ").strip().upper()
    achou = db.consultar(
        "SELECT resultado FROM ocorrencias WHERE id = :i", {"i": id_ocorrencia})
    if not achou:
        print("Ocorrencia nao encontrada.")
        return
    if achou[0]["resultado"] == "falso_positivo":
        print("Ja marcada como falso-positivo.")
        return
    db.executar("""UPDATE ocorrencias SET resultado = 'falso_positivo',
                   classificacao = 'normal' WHERE id = :i""", {"i": id_ocorrencia})
    print("[Odisperso] Corrigido como falso-positivo.")


# ---------------- DELETE ----------------
def excluir_ocorrencia():
    id_ocorrencia = input("ID da ocorrencia: ").strip().upper()
    achou = db.consultar("SELECT * FROM ocorrencias WHERE id = :i", {"i": id_ocorrencia})
    if not achou:
        print("Ocorrencia nao encontrada.")
        return
    print(f"\nOcorrencia: {achou[0]['id']} | {achou[0]['data']}")
    try:
        if int(input("Excluir? 1-Sim / 2-Nao: ")) == 1:
            db.executar("DELETE FROM ocorrencias WHERE id = :i", {"i": id_ocorrencia})
            print("[Odisperso] Ocorrencia excluida.")
        else:
            print("Exclusao cancelada.")
    except ValueError:
        print("Opcao invalida.")
