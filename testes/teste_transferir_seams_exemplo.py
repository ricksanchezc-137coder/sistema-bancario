from datetime import datetime
from security import registrar_usuario
from servico import depositar, transferir
from banco import buscar_um


def test_transferir_grava_data_hora_exata(conn):
    """
    RED: hoje `transferir` não aceita `agora`, então essa chamada
    deve falhar com TypeError (unexpected keyword argument 'agora').
    Isso é esperado nesse estágio — é o ponto de partida, não um bug.
    """
    registrar_usuario("joao_origem", "Senha@123")
    registrar_usuario("joao_destino", "Senha@123")

    conta_origem_row = buscar_um(
        """
        SELECT contas.id FROM contas
        JOIN usuarios ON contas.usuario_id = usuarios.id
        WHERE usuarios.nome = ?
        """,
        ("joao_origem",),
    )
    conta_origem_id = conta_origem_row["id"]

    depositar(conta_origem_id, 500.0)

    agora_fixo = datetime(2024, 1, 15, 12, 30, 0)

    transferir(
        origem_id=conta_origem_id,
        destino_nome="joao_destino",
        valor=100.0,
        agora=agora_fixo,
    )

    cursor = conn.cursor()
    cursor.execute(
        "SELECT data_hora FROM transacoes WHERE conta_origem_id = ? ORDER BY id DESC LIMIT 1",
        (conta_origem_id,),
    )
    data_hora_gravada = cursor.fetchone()["data_hora"]

    assert data_hora_gravada == agora_fixo.isoformat()
