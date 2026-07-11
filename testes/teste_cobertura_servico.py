
import pytest
import servico_v2 as sv
import security
from dados import LIMITE_SAQUE


def _obter_conta_id(conn, nome):
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT contas.id FROM contas
        JOIN usuarios ON contas.usuario_id = usuarios.id
        WHERE usuarios.nome = ?
        """,
        (nome,),
    )
    return cursor.fetchone()["id"]


def _criar_usuario_com_conta(conn, nome, senha="Senha123!"):
    security.registrar_usuario(nome, senha)
    return _obter_conta_id(conn, nome)


# ---- linha 23: obter_conta -> não encontrada ----
def test_obter_conta_inexistente_levanta_erro(conn):
    cursor = conn.cursor()
    with pytest.raises(ValueError, match="Conta não encontrada"):
        sv.obter_conta(cursor, 999999)


# ---- linha 66: verificar_consistencia -> saldo inconsistente ----
def test_verificar_consistencia_detecta_inconsistencia(conn):
    conta_id = _criar_usuario_com_conta(conn, "usuario_consistencia")
    sv.depositar(conta_id, 100.0)

    cursor = conn.cursor()
    cursor.execute("UPDATE contas SET saldo = ? WHERE id = ?", (99999.0, conta_id))
    conn.commit()

    with pytest.raises(Exception, match="Inconsistência"):
        sv.verificar_consistencia(cursor, conta_id)


# ---- linha 106: sacar -> limite excedido ----
def test_sacar_acima_do_limite_levanta_erro(conn):
    conta_id = _criar_usuario_com_conta(conn, "usuario_limite")
    sv.depositar(conta_id, LIMITE_SAQUE * 2)

    with pytest.raises(ValueError, match="Limite de saque excedido"):
        sv.sacar(conta_id, LIMITE_SAQUE + 1)


# ---- linha 141: transferir -> usuário destino não encontrado ----
def test_transferir_destino_inexistente_levanta_erro(conn):
    origem_id = _criar_usuario_com_conta(conn, "usuario_origem_141")
    sv.depositar(origem_id, 100.0)

    with pytest.raises(ValueError, match="Usuário de destino não encontrado"):
        sv.transferir(origem_id, "usuario_que_nao_existe_xyz", 10.0)


# ---- linha 150: transferir -> conta de destino não encontrada ----
def test_transferir_usuario_sem_conta_levanta_erro(conn):
    origem_id = _criar_usuario_com_conta(conn, "usuario_origem_150")
    sv.depositar(origem_id, 100.0)

    security.registrar_usuario("usuario_sem_conta", "Senha123!")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM usuarios WHERE nome = ?", ("usuario_sem_conta",))
    usuario_id = cursor.fetchone()["id"]
    cursor.execute("DELETE FROM contas WHERE usuario_id = ?", (usuario_id,))
    conn.commit()

    with pytest.raises(ValueError, match="Conta de destino não encontrada"):
        sv.transferir(origem_id, "usuario_sem_conta", 10.0)


# ---- linha 155: transferir -> transferência para si mesmo ----
def test_transferir_para_si_mesmo_levanta_erro(conn):
    conta_id = _criar_usuario_com_conta(conn, "usuario_155")
    sv.depositar(conta_id, 100.0)

    with pytest.raises(ValueError, match="Transferência para si mesmo"):
        sv.transferir(conta_id, "usuario_155", 10.0)
