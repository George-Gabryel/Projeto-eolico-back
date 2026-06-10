
import pandas as pd
import database as db
import funcoes_usuarios as fun_user


# ---------------- CREATE ----------------
def cadastrar_parque():
    print("\n--- CADASTRO DE PARQUE EOLICO ---")

    while True:
        id_parque = input("ID do parque (ex: PARQ-001): ").strip().upper()
        if id_parque == "":
            print("ID nao pode ser vazio.")
            continue
        existe = db.consultar("SELECT id FROM parques WHERE id = :i", {"i": id_parque})
        if existe:
            print("ID ja cadastrado.")
            continue
        break

    # Vincular a um cliente ja cadastrado
    clientes = fun_user.listar_clientes()
    if not clientes:
        print("Nao ha clientes cadastrados. Cadastre um cliente antes.")
        return
    print("\nClientes disponiveis:")
    for c in clientes:
        print(f"  - {c['email']}  ({c['usuario']})")
    while True:
        email_cliente = input("E-mail do cliente dono do parque: ").strip()
        if any(c["email"] == email_cliente for c in clientes):
            break
        print("E-mail nao corresponde a um cliente cadastrado.")

    nome      = input("Nome do parque: ").strip()
    operadora = input("Operadora: ").strip()
    estado    = input("Estado/Regiao: ").strip()

    while True:
        try:
            capacidade_total = float(input("Capacidade total (MW): "))
            if capacidade_total > 0:
                break
            print("Deve ser maior que 0.")
        except ValueError:
            print("Digite um numero valido.")

    while True:
        try:
            prod = float(input(f"Producao atual (0 a {capacidade_total} MW): "))
            if 0 <= prod <= capacidade_total:
                break
            print(f"Entre 0 e {capacidade_total}.")
        except ValueError:
            print("Digite um numero valido.")

    while True:
        try:
            vento = float(input("Velocidade media do vento (km/h): "))
            if vento >= 0:
                break
            print("Deve ser >= 0.")
        except ValueError:
            print("Digite um numero valido.")

    efic = round((prod / capacidade_total) * 100, 2) if capacidade_total > 0 else 0.0

    db.executar("""
        INSERT INTO parques (id, nome, operadora, estado,
            capacidade_total_mw, producao_atual_mw, eficiencia,
            velocidade_vento_media, status, email_cliente)
        VALUES (:id, :nome, :op, :est, :capacidade_total, :prod, :ef, :vento, 'ativo', :cli)
    """, {
        "id": id_parque, "nome": nome, "op": operadora, "est": estado,
        "capacidade_total": capacidade_total, "prod": prod, "ef": efic, "vento": vento,
        "cli": email_cliente
    })
    print(f"\n[OK] Parque '{id_parque} - {nome}' cadastrado e vinculado a {email_cliente}!")


# ---------------- READ ----------------
def visualizar_parques(email_cliente=None):
    """
    Se email_cliente for informado, mostra apenas os parques daquele cliente.
    Caso contrario, mostra todos (Gerente / Funcionario).
    """
    print("\n--- LISTA DE PARQUES ---")
    if email_cliente:
        parques = db.consultar(
            "SELECT * FROM parques WHERE email_cliente = :c",
            {"c": email_cliente})
    else:
        parques = db.consultar("SELECT * FROM parques")

    if not parques:
        print("Nenhum parque encontrado.")
        return

    for p in parques:
        tag = "[DESATIVADO]" if p["status"] == "desativado" else "[ATIVO]"
        print(f"\n{tag} {p['id']} - {p['nome']}")
        print(f"  Operadora      : {p['operadora']}")
        print(f"  Estado         : {p['estado']}")
        print(f"  Capacidade     : {p['capacidade_total_mw']} MW")
        print(f"  Producao atual : {p['producao_atual_mw']} MW")
        print(f"  Eficiencia     : {p['eficiencia']}%")
        print(f"  Vento medio    : {p['velocidade_vento_media']} km/h")
        print(f"  Cliente dono   : {p['email_cliente']}")


def dashboard_parque(email_cliente=None):
    print("\n--- DASHBOARD DO PARQUE ---")
    id_parque = input("ID do parque: ").strip().upper()
    if email_cliente:
        achou = db.consultar(
            "SELECT * FROM parques WHERE id = :i AND email_cliente = :c",
            {"i": id_parque, "c": email_cliente})
    else:
        achou = db.consultar("SELECT * FROM parques WHERE id = :i", {"i": id_parque})

    if not achou:
        print("Parque nao encontrado (ou nao pertence a voce).")
        return

    p = achou[0]
    ef = p["eficiencia"]
    classe = ("EXCELENTE" if ef >= 80 else "BOM" if ef >= 60
              else "REGULAR" if ef >= 40 else "CRITICO")
    barra_cheia = int(min(ef / 100, 1.0) * 20)
    barra = "#" * barra_cheia + "-" * (20 - barra_cheia)

    print(f"\n==================================================")
    print(f"  DASHBOARD - {p['id']} | {p['nome']}")
    print(f"==================================================")
    print(f"  Operadora      : {p['operadora']}")
    print(f"  Estado         : {p['estado']}")
    print(f"  Status         : {p['status'].upper()}")
    print(f"  Capacidade     : {p['capacidade_total_mw']} MW")
    print(f"  Producao atual : {p['producao_atual_mw']} MW")
    print(f"  Aproveitamento : [{barra}] {ef}% -> {classe}")
    print(f"  Vento medio    : {p['velocidade_vento_media']} km/h")
    print(f"==================================================")


def estatisticas_parques():
    """Painel com Pandas: usa o DataFrame para medias e ranking."""
    print("\n--- ESTATISTICAS GERAIS DOS PARQUES ---")
    parques = db.consultar("SELECT * FROM parques")
    if not parques:
        print("Nenhum parque cadastrado.")
        return

    df = pd.DataFrame(parques)

    ativos     = (df["status"] == "ativo").sum()
    cap_total  = df["capacidade_total_mw"].sum()
    prod_total = df["producao_atual_mw"].sum()
    ef_media   = df["eficiencia"].mean()
    ef_max     = df["eficiencia"].max()
    ef_min     = df["eficiencia"].min()
    vento_med  = df["velocidade_vento_media"].mean()

    print(f"\n==================================================")
    print(f"  VISAO GERAL - {len(df)} parque(s)")
    print(f"==================================================")
    print(f"  Ativos            : {ativos}")
    print(f"  Capacidade total  : {cap_total:.1f} MW")
    print(f"  Producao total    : {prod_total:.1f} MW")
    print(f"  Eficiencia media  : {ef_media:.1f}%")
    print(f"  Eficiencia max/min: {ef_max:.1f}% / {ef_min:.1f}%")
    print(f"  Vento medio geral : {vento_med:.1f} km/h")
    print(f"--------------------------------------------------")
    print("  Ranking de eficiencia:")
    ranking = df.sort_values("eficiencia", ascending=False).reset_index(drop=True)
    for i, linha in ranking.iterrows():
        print(f"    {i+1}. {linha['id']}  {linha['eficiencia']}%  ({linha['status']})")
    print(f"==================================================")


# ---------------- UPDATE ----------------
def atualizar_producao():
    id_parque = input("ID do parque: ").strip().upper()
    achou = db.consultar("SELECT * FROM parques WHERE id = :i", {"i": id_parque})
    if not achou:
        print("Parque nao encontrado.")
        return
    capacidade_total = achou[0]["capacidade_total_mw"]
    print(f"Producao atual: {achou[0]['producao_atual_mw']} MW | Capacidade: {capacidade_total} MW")
    while True:
        try:
            p = float(input(f"Nova producao (0 a {capacidade_total} MW): "))
            if 0 <= p <= capacidade_total:
                ef = round((p / capacidade_total) * 100, 2)
                db.executar("""UPDATE parques SET producao_atual_mw = :p,
                               eficiencia = :ef WHERE id = :i""",
                            {"p": p, "ef": ef, "i": id_parque})
                print(f"[OK] Producao atualizada! Eficiencia: {ef}%")
                return
            print(f"Entre 0 e {capacidade_total}.")
        except ValueError:
            print("Numero valido.")


def atualizar_configuracoes():
    id_parque = input("ID do parque: ").strip().upper()
    achou = db.consultar("SELECT * FROM parques WHERE id = :i", {"i": id_parque})
    if not achou:
        print("Parque nao encontrado.")
        return
    print(f"\nParque: {achou[0]['id']} - {achou[0]['nome']}")
    print("1 - Nome\n2 - Operadora\n3 - Velocidade do vento")
    try:
        escolha = int(input("Escolha: "))
    except ValueError:
        print("Opcao invalida.")
        return
    if escolha == 1:
        novo = input("Novo nome: ").strip()
        db.executar("UPDATE parques SET nome = :n WHERE id = :i",
                    {"n": novo, "i": id_parque})
        print("[OK] Nome atualizado!")
    elif escolha == 2:
        novo = input("Nova operadora: ").strip()
        db.executar("UPDATE parques SET operadora = :n WHERE id = :i",
                    {"n": novo, "i": id_parque})
        print("[OK] Operadora atualizada!")
    elif escolha == 3:
        while True:
            try:
                v = float(input("Nova velocidade (km/h): "))
                if v >= 0:
                    db.executar("""UPDATE parques SET velocidade_vento_media = :v
                                   WHERE id = :i""", {"v": v, "i": id_parque})
                    print("[OK] Velocidade atualizada!")
                    return
                print("Deve ser >= 0.")
            except ValueError:
                print("Numero valido.")
    else:
        print("Opcao invalida.")


# ---------------- DELETE ----------------
def remover_ou_desativar_parque():
    id_parque = input("ID do parque: ").strip().upper()
    achou = db.consultar("SELECT * FROM parques WHERE id = :i", {"i": id_parque})
    if not achou:
        print("Parque nao encontrado.")
        return
    print(f"\nParque: {achou[0]['id']} - {achou[0]['nome']}")
    print("1 - Desativar (mantem historico)")
    print("2 - Remover completamente")
    print("3 - Cancelar")
    try:
        escolha = int(input("Escolha: "))
    except ValueError:
        print("Opcao invalida.")
        return
    if escolha == 1:
        db.executar("UPDATE parques SET status = 'desativado' WHERE id = :i",
                    {"i": id_parque})
        print("[OK] Parque desativado. Historico mantido.")
    elif escolha == 2:
        print("1 - Sim\n2 - Cancelar")
        try:
            conf = int(input("Confirmar remocao total? "))
        except ValueError:
            print("Opcao invalida.")
            return
        if conf == 1:
            db.executar("DELETE FROM parques WHERE id = :i", {"i": id_parque})
            print("[OK] Parque removido.")
        else:
            print("Remocao cancelada.")
    elif escolha == 3:
        print("Operacao cancelada.")
    else:
        print("Opcao invalida.")
