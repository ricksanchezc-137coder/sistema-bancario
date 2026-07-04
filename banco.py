import sqlite3
from dados import DB_NAME

def conectar():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def criar_tabelas():
    with conectar() as conn:
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS contas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            saldo REAL DEFAULT 0,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            conta_origem_id INTEGER,
            conta_destino_id INTEGER,
            valor REAL NOT NULL,
            saldo_apos REAL,
            data_hora TEXT NOT NULL,
        
            FOREIGN KEY (conta_origem_id) REFERENCES contas(id),
            FOREIGN KEY (conta_destino_id) REFERENCES contas(id)
        )
        """)

def executar(sql, params=None):
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params or ())
        return cursor

def buscar_um(sql, params=None):
    cursor = executar(sql, params)
    return cursor.fetchone()

def buscar_todos(sql, params=None):
    cursor = executar(sql, params)
    return cursor.fetchall()

def executar_transacao(operacao):
    conn = conectar()
    conn.isolation_level = None
    cursor = conn.cursor()

    try:
        cursor.execute("BEGIN")
        operacao(cursor)
        conn.commit()

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        conn.close()

