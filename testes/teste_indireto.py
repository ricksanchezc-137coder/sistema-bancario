import pytest
from security import registrar_usuario
from servico_v2 import depositar, verificar_consistencia


@pytest.fixture
def conta_configurada(request, conn):
    """Cria um usuário/conta e aplica o saldo_inicial recebido via request.param."""
    saldo_inicial = request.param
    nome = "usuario_indireto"

    registrar_usuario(nome, "Senha@123")

    cursor = conn.cursor()
    cursor.execute(
        "SELECT contas.id FROM contas "
        "JOIN usuarios ON contas.usuario_id = usuarios.id "
        "WHERE usuarios.nome = ?",
        (nome,)
    )
    conta_id = cursor.fetchone()[0]

    if saldo_inicial > 0:
        depositar(conta_id, saldo_inicial)

    return conta_id

@pytest.mark.parametrize("conta_configurada", [100], indirect=True)
def test_conta_configurada_saldo_100(conta_configurada, conn):
    cursor = conn.cursor()
    verificar_consistencia(cursor, conta_configurada)  # não lança = consistente
    try:
        verificar_consistencia(cursor, conta_configurada)
    except Exception:
        pytest.fail("Inconsistência detectada")

@pytest.mark.parametrize("conta_configurada", [0, 100, 5000], indirect=True)
def test_conta_configurada_varios_saldos(conta_configurada, conn):
    cursor = conn.cursor()
    verificar_consistencia(cursor, conta_configurada)


@pytest.fixture
def conta_zerada(conn):
    nome = "usuario_zerado"
    registrar_usuario(nome, "Senha@123")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT contas.id FROM contas "
        "JOIN usuarios ON contas.usuario_id = usuarios.id "
        "WHERE usuarios.nome = ?",
        (nome,)
    )
    return cursor.fetchone()[0]


@pytest.mark.parametrize("valor_invalido", [-50, -1, 0])
def test_depositar_valor_invalido_lanca_valueerror(conta_zerada, valor_invalido):
    with pytest.raises(ValueError):
        depositar(conta_zerada, valor_invalido)



