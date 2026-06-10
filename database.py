

from sqlalchemy import create_engine, text


engine = create_engine("sqlite:///sistema.db")


def executar(sql, parametros=None):
  
    try:
        with engine.begin() as conexao:
            conexao.execute(text(sql), parametros or {})
        return True
    except Exception as erro:
        print("Erro no banco de dados:", erro)
        return False


def consultar(sql, parametros=None):
  
    try:
        with engine.connect() as conexao:
            resultado = conexao.execute(text(sql), parametros or {})
            linhas = resultado.mappings().all()
            return [dict(linha) for linha in linhas]
    except Exception as erro:
        print("Erro no banco de dados:", erro)
        return []


def criar_tabelas():
 
    # ---- USUARIOS ----
    executar("""
        CREATE TABLE IF NOT EXISTS usuarios (
            email       TEXT PRIMARY KEY,
            usuario     TEXT,
            telefone    TEXT,
            senha       TEXT,
            tipo_perfil TEXT
        )
    """)

    # ---- PARQUES (cada parque pertence a um cliente, via email_cliente) ----
    executar("""
        CREATE TABLE IF NOT EXISTS parques (
            id                     TEXT PRIMARY KEY,
            nome                   TEXT,
            operadora              TEXT,
            estado                 TEXT,
            capacidade_total_mw    REAL,
            producao_atual_mw      REAL,
            eficiencia             REAL,
            velocidade_vento_media REAL,
            status                 TEXT,
            email_cliente          TEXT
        )
    """)

    # ---- TURBINAS ----
    executar("""
        CREATE TABLE IF NOT EXISTS turbinas (
            id             TEXT PRIMARY KEY,
            id_parque      TEXT,
            modelo         TEXT,
            fabricante     TEXT,
            capacidade_mw  REAL,
            horas_operacao INTEGER,
            status         TEXT
        )
    """)

    # ---- DRONES ----
    executar("""
        CREATE TABLE IF NOT EXISTS drones (
            id           TEXT PRIMARY KEY,
            id_parque    TEXT,
            nome         TEXT,
            bateria_lipo INTEGER,
            limite_voo   INTEGER,
            status       TEXT
        )
    """)

    # ---- OCORRENCIAS ----
    executar("""
        CREATE TABLE IF NOT EXISTS ocorrencias (
            id              TEXT PRIMARY KEY,
            id_parque       TEXT,
            id_turbina      TEXT,
            data            TEXT,
            tipo_ave        TEXT,
            quantidade_aves INTEGER,
            metodo          TEXT,
            eficacia        INTEGER,
            resultado       TEXT,
            classificacao   TEXT
        )
    """)

    # ---- RELATORIOS ----
    executar("""
        CREATE TABLE IF NOT EXISTS relatorios (
            id                 TEXT PRIMARY KEY,
            id_parque          TEXT,
            nome               TEXT,
            tipo               TEXT,
            num_ocorrencias    INTEGER,
            eficacia_media     REAL,
            economia_estimada  REAL,
            status             TEXT
        )
    """)
