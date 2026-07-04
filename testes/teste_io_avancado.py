import pytest
import banco
from main import obter_conta, menu
from servico_v2 import depositar, calcular_saldo


def test_opcao_1_mostra_saldo(capsys, monkeypatch, usuario_autenticado):
    conta = obter_conta(usuario_autenticado.id)

    respostas = iter(["1", "0"])
    monkeypatch.setattr("builtins.input", lambda _: next(respostas))

    menu(conta)

    captured = capsys.readouterr()
    assert "Saldo:" in captured.out


def test_saldo_apos_depositos_fracionados(usuario_autenticado):
    conta = obter_conta(usuario_autenticado.id)

    depositar(conta.id, 10.10)
    depositar(conta.id, 20.20)

    conn = banco.conectar()
    cursor = conn.cursor()
    saldo = calcular_saldo(cursor, conta.id)
    conn.close()

    assert saldo == pytest.approx(30.30)
