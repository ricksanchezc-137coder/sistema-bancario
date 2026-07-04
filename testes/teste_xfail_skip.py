import sys
import pytest


def somar(a, b):
    return a + b


def funcao_nao_implementada():
    raise NotImplementedError("ainda não implementado")


class TestSkip:
    @pytest.mark.skip(reason="funcionalidade removida temporariamente")
    def test_skip_simples(self):
        assert False

    @pytest.mark.skipif(sys.version_info < (3, 11), reason="requer Python 3.11+")
    def test_skipif_versao_python(self):
        # No Termux (3.13) executa. No Pyto (3.10) pula.
        assert True

    def test_skip_imperativo(self):
        if sys.version_info < (3, 11):
            pytest.skip("recurso indisponível nesta versão")
        assert True


class TestXfail:
    @pytest.mark.xfail(reason="bug conhecido: função não implementada")
    def test_xfail_simples(self):
        funcao_nao_implementada()

    @pytest.mark.xfail(reason="deve continuar falhando", strict=True)
    def test_xfail_strict_falha(self):
        assert somar(2, 2) == 5

    @pytest.mark.xfail(reason="instável, se passar quero saber sem quebrar a suite")
    def test_xfail_pode_passar(self):
        assert somar(2, 2) == 4

    @pytest.mark.xfail(reason="acho que ainda falha, strict pra confirmar", strict=True)
    def test_xfail_strict_mas_passa(self):
        assert somar(2, 2) == 4

    def test_xfail_imperativo(self):
        if somar(1, 1) != 3:
            pytest.xfail("resultado inesperado, falha esperada")
        assert False
