from servico_v2 import calcular_saldo
def test_calcular_saldo_ignora_tipo_desconhecido(conn):
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO usuarios (nome, senha) VALUES (?, ?)",
        ("usuario_tipo_invalido", "hash_fake"),
    )
    usuario_id = cursor.lastrowid

    cursor.execute(
        "INSERT INTO contas (usuario_id, saldo) VALUES (?, ?)",
        (usuario_id, 0),
    )
    conta_id = cursor.lastrowid

    # tipo que não bate com nenhuma das 4 constantes esperadas
    cursor.execute(
        """
        INSERT INTO transacoes (tipo, conta_origem_id, conta_destino_id, valor, data_hora)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("TIPO_INEXISTENTE", conta_id, None, 100.0, "2026-07-05T13:40:00"),
    )
    conn.commit()

    saldo = calcular_saldo(cursor, conta_id)

    assert saldo == 0  # nenhum if/elif bateu, saldo permanece inalterado
