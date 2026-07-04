
import pytest

import security


# ══════════════════════════════════════════════
# TESTES — dependência entre fixtures
# ══════════════════════════════════════════════

def test_nivel_1_banco_criado(banco_temp):
    pass  # banco criado sem erro = sucesso


def test_nivel_2_usuario_retornado(usuario_registrado):
    assert usuario_registrado == "joao"


def test_nivel_3_login_retorna_resultado(usuario_autenticado):
    # ajuste o assert conforme o retorno real de login()
    assert usuario_autenticado is not None


def test_cadeia_banco_isolado_a(usuario_registrado):
    """Banco A — isolado por tempdir."""
    assert usuario_registrado == "joao"


def test_cadeia_banco_isolado_b(usuario_registrado):
    """Banco B — sem contaminação do banco A."""
    assert usuario_registrado == "joao"


# ══════════════════════════════════════════════
# TESTES — autouse=True
# ══════════════════════════════════════════════

def test_autouse_sem_declarar():
    """autouse não foi listado — rodou mesmo assim."""
    assert len(security.tentativas_login) == 0


def test_autouse_coexiste_com_fixture(banco_temp):
    """autouse + outra fixture — ambas ativas."""
    assert len(security.tentativas_login) == 0


def test_autouse_isola_estado():
    """Modifica tentativas — autouse limpa no cleanup."""
    security.tentativas_login["joao"] = 2
    assert security.tentativas_login["joao"] == 2


def test_autouse_proxima_execucao_zerada():
    """Autouse limpou antes deste teste — estado está zerado."""
    assert "joao" not in security.tentativas_login

