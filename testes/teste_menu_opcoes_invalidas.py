import pytest
from unittest.mock import MagicMock
import main


@pytest.mark.parametrize(
    "entradas, mensagem_esperada",
    [
        (["9", "0"], "Opção inválida"),
        (["abc", "0"], "Opção inválida"),
        (["5", "9", "0"], "Opcao Invalida"),
        (["5", "abc", "0"], "Opcao Invalida"),
        (["5", "3", "9", "0"], "Opcao invalida"),
        (["5", "3", "abc", "0"], "Opcao invalida"),
    ],
)
def teste_menu_opcao_invalida(monkeypatch, capsys, entradas, mensagem_esperada):
    conta_mock = MagicMock()
    conta_mock.id = 1
    conta_mock.usuario_id = 1
    conta_mock.saldo = 100.0

    entradas_iter = iter(entradas)
    monkeypatch.setattr("builtins.input", lambda _: next(entradas_iter))

    main.menu(conta_mock)

    saida = capsys.readouterr().out
    assert mensagem_esperada in saida
