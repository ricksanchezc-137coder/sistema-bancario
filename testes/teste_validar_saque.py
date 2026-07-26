from servico import validar_saque
import pytest
def test_saque_valido_retorna_saldo_correto():
    novo_saldo = validar_saque(saldo=100, valor=30)
    assert novo_saldo == 70
def test_saque_com_saldo_insuficiente_levanta_erro():
    with pytest.raises(ValueError):
        validar_saque(saldo=50, valor=100)
def test_saque_acima_do_limite_levanta_erro():
    from dados import LIMITE_SAQUE
    with pytest.raises(ValueError):
        validar_saque(saldo=999999, valor = LIMITE_SAQUE + 1)
