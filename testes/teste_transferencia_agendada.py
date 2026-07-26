import pytest
from datetime import date, timedelta
from security import registrar_usuario
from servico import agendar_transferencia, depositar, executar_transferencias_vencidas
from banco import buscar_um, executar


def test_agendar_transferencia_futura_fica_pendente(conn):
    """
    Agendar uma transferencia com data futura deve gravar o registro
    com status 'pendente' no banco.
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

    data_agendada = date.today() + timedelta(days=5)

    agendar_transferencia(
        origem_id=conta_origem_id,
        destino_nome="joao_destino",
        valor=100.0,
        data_agendada=data_agendada,
    )

    cursor = conn.cursor()
    cursor.execute(
        "SELECT status, data_agendada FROM transferencias_agendadas "
        "WHERE conta_origem_id = ? ORDER BY id DESC LIMIT 1",
        (conta_origem_id,),
    )
    row = cursor.fetchone()

    assert row["status"] == "pendente"
    assert row["data_agendada"] == data_agendada.isoformat()

def test_agendar_transferencia_data_passada_gera_erro(conn):
    """
    Agendar uma transferencia com data no passado deve levantar
    ValueError.
    """
    registrar_usuario("joao_origem2", "Senha@123")
    registrar_usuario("joao_destino2", "Senha@123")

    conta_origem_row = buscar_um(
        """
        SELECT contas.id FROM contas
        JOIN usuarios ON contas.usuario_id = usuarios.id
        WHERE usuarios.nome = ?
        """,
        ("joao_origem2",),
    )
    conta_origem_id = conta_origem_row["id"]

    depositar(conta_origem_id, 500.0)

    data_passada = date.today() - timedelta(days=1)

    with pytest.raises(ValueError):
        agendar_transferencia(
            origem_id=conta_origem_id,
            destino_nome="joao_destino2",
            valor=100.0,
            data_agendada=data_passada,
        )

def test_executar_transferencias_vencidas_executa_de_verdade(conn):
    """
    Uma transferencia agendada com data vencida, ao ser processada por
    executar_transferencias_vencidas(), deve debitar a origem, creditar
    o destino e marcar status como 'executada'.
    """
    registrar_usuario("joao_origem3", "Senha@123")
    registrar_usuario("joao_destino3", "Senha@123")

    conta_origem_row = buscar_um(
        """
        SELECT contas.id FROM contas
        JOIN usuarios ON contas.usuario_id = usuarios.id
        WHERE usuarios.nome = ?
        """,
        ("joao_origem3",),
    )
    conta_origem_id = conta_origem_row["id"]

    conta_destino_row = buscar_um(
        """
        SELECT contas.id FROM contas
        JOIN usuarios ON contas.usuario_id = usuarios.id
        WHERE usuarios.nome = ?
        """,
        ("joao_destino3",),
    )
    conta_destino_id = conta_destino_row["id"]

    depositar(conta_origem_id, 500.0)

    data_vencida = date.today() - timedelta(days=1)

    executar(
        """
        INSERT INTO transferencias_agendadas
        (conta_origem_id, conta_destino_id, valor, data_agendada, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        (conta_origem_id, conta_destino_id, 100.0, data_vencida.isoformat(), "pendente")
    )

    executar_transferencias_vencidas()

    saldo_origem = buscar_um(
        "SELECT saldo FROM contas WHERE id = ?",       (conta_origem_id,)
    )
    saldo_destino = buscar_um(
        "SELECT saldo FROM contas WHERE id = ?", (conta_destino_id,)
    )

    assert saldo_origem["saldo"] == 400.0
    assert saldo_destino["saldo"] == 100.0

    status_row = buscar_um(
        "SELECT status FROM transferencias_agendadas WHERE conta_origem_id = ?",
        (conta_origem_id,),
    )
    assert status_row["status"] == "executada"


def test_executar_transferencias_vencidas_nao_executa_duas_vezes(conn):
    """
    Requisito 4: chamar executar_transferencias_vencidas() duas vezes não pode
    debitar/creditar a mesma transferência duas vezes.
    """
    registrar_usuario("joao_origem4", "Senha@123")
    registrar_usuario("joao_destino4", "Senha@123")

    conta_origem_row = buscar_um(
        """
        SELECT contas.id FROM contas
        JOIN usuarios ON contas.usuario_id = usuarios.id
        WHERE usuarios.nome = ?
        """,
        ("joao_origem4",),
    )
    conta_origem_id = conta_origem_row["id"]

    conta_destino_row = buscar_um(
        """
        SELECT contas.id FROM contas
        JOIN usuarios ON contas.usuario_id = usuarios.id
        WHERE usuarios.nome = ?
        """,
        ("joao_destino4",),
    )
    conta_destino_id = conta_destino_row["id"]

    depositar(conta_origem_id, 500.0)

    data_vencida = date.today() - timedelta(days=1)

    executar(
        """
        INSERT INTO transferencias_agendadas
        (conta_origem_id, conta_destino_id, valor, data_agendada, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        (conta_origem_id, conta_destino_id, 100.0, data_vencida.isoformat(), "pendente"),
    )

    executar_transferencias_vencidas()
    executar_transferencias_vencidas()

    saldo_origem = buscar_um(
        "SELECT saldo FROM contas WHERE id = ?", (conta_origem_id,)
    )
    saldo_destino = buscar_um(
        "SELECT saldo FROM contas WHERE id = ?", (conta_destino_id,)
    )

    assert saldo_origem["saldo"] == 400.0
    assert saldo_destino["saldo"] == 100.0
