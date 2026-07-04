import pytest
import servico_v2
import banco


def test_validar_valor_chamado_no_deposito(mocker, banco_temp, usuario_registrado):
    conta = banco.buscar_um(
        "SELECT contas.id FROM contas JOIN usuarios ON contas.usuario_id = usuarios.id WHERE usuarios.nome = ?",
        (usuario_registrado,)
    )
    conta_id = conta["id"]

    spy = mocker.spy(servico_v2, "validar_valor")

    servico_v2.depositar(conta_id=conta_id, valor=150.0)

    spy.assert_called_once_with(150.0)
    assert spy.spy_return is None


def test_depositar_propaga_erro_em_executar_transacao(mocker, banco_temp, usuario_registrado):
    conta = banco.buscar_um(
        "SELECT contas.id FROM contas JOIN usuarios ON contas.usuario_id = usuarios.id WHERE usuarios.nome = ?",
        (usuario_registrado,)
    )
    conta_id = conta["id"]

    mocker.patch(
        "servico_v2.executar_transacao",
        side_effect=RuntimeError("Falha simulada na transação")
    )

    with pytest.raises(RuntimeError, match="Falha simulada na transação"):
        servico_v2.depositar(conta_id=conta_id, valor=100.0)



def test_depositar_conta_inexistente(mocker, banco_temp):
    mocker.patch.object(
        servico_v2,
        "obter_conta",
        side_effect=ValueError("Conta não encontrada")
    )

    with pytest.raises(ValueError, match="Conta não encontrada"):
        servico_v2.depositar(conta_id=999, valor=50.0)


def test_obter_conta_com_cursor_mockado(mocker):
    cursor_mock = mocker.Mock()
    cursor_mock.fetchone.return_value = {"id": 1, "usuario_id": 10, "saldo": 500.0}

    conta = servico_v2.obter_conta(cursor_mock, conta_id=1)

    cursor_mock.execute.assert_called_once_with(
        "SELECT id, usuario_id, saldo FROM contas WHERE id = ?",
        (1,)
    )
    assert conta.id == 1
    assert conta.usuario_id == 10
    assert conta.saldo == 500.0
