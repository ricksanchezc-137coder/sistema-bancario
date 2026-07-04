import pytest
import tempfile
import os
from unittest.mock import patch
import banco
from banco import criar_tabelas
from servico_v2 import depositar

_log = []  # rastreia quantas vezes cada fixture é inicializada

# ─── scope: function (padrão) ─────────────────
@pytest.fixture(scope="function")
def db_func():
    _log.append("function")
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "banco.db")
        with patch("banco.DB_NAME", db_path):
            criar_tabelas()
            yield db_path

# ─── scope: module ────────────────────────────
@pytest.fixture(scope="module")
def db_mod():
    _log.append("module")
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "banco.db")
        with patch("banco.DB_NAME", db_path):
            criar_tabelas()
            yield db_path

# 3 testes com db_func → fixture criada 3x
def test_func_a(db_func): assert os.path.exists(db_func)
def test_func_b(db_func): assert os.path.exists(db_func)
def test_func_c(db_func): assert os.path.exists(db_func)

# 3 testes com db_mod → fixture criada apenas 1x
def test_mod_a(db_mod): assert os.path.exists(db_mod)
def test_mod_b(db_mod): assert os.path.exists(db_mod)
def test_mod_c(db_mod): assert os.path.exists(db_mod)

def test_contar_setups():
    # Prova concreta da diferença de escopo
    assert _log.count("function") == 3
    assert _log.count("module") == 1

# ─── params= ──────────────────────────────────
@pytest.fixture(params=[100.0, 250.0, 1000.0])
def valor(request):
    return request.param

# Este teste roda 3 vezes automaticamente
def test_depositar_com_params(valor):
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "banco.db")
        with patch("banco.DB_NAME", db_path):
            criar_tabelas()
            with banco.conectar() as conn:
                conn.execute("INSERT INTO usuarios(nome, senha) VALUES(?, ?)", ("Ana", "1234"))
                conn.execute("INSERT INTO contas(usuario_id, saldo) VALUES(?, 0)", (1,))
            depositar(1, valor)

