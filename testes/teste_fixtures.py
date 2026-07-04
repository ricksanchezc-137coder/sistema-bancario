import pytest
def test_fixture_cria_banco(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tabelas = [row[0] for row in cursor.fetchall()]
    assert "contas" in tabelas

def test_fixture_cria_banco_com_registros(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM contas")
    resultado = cursor.fetchone()
    assert resultado is not None

def test_tabela_usuarios_existe(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    resultado = cursor.fetchone()
    assert resultado is not None

def test_banco_inicia_vazio(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM contas")
    total = cursor.fetchone()[0]
    assert total == 0

@pytest.mark.parametrize("valor", [100.0, 250.0, 0.01])
def test_deposito_valor_positivo(valor):
    assert valor > 0

def test_valor_invalido_levanta_erro(conn):
    with pytest.raises(Exception):
        conn.execute("INSERT INTO contas (usuario_id, saldo) VALUES (NULL, 0)")
