
import pytest
import sqlite3
import tempfile
import os
from unittest.mock import patch
from banco import criar_tabelas
import security
from security import registrar_usuario, login


@pytest.fixture
def conn():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        with patch("banco.DB_NAME", db_path):
            criar_tabelas()
            connection = sqlite3.connect(db_path)
            connection.row_factory = sqlite3.Row
            yield connection
            connection.close()


@pytest.fixture
def banco_temp():
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch("banco.DB_NAME", os.path.join(tmpdir, "test.db")):
            criar_tabelas()
            yield


@pytest.fixture
def usuario_registrado(banco_temp):
    registrar_usuario("joao", "Senha@123")
    return "joao"


@pytest.fixture
def usuario_autenticado(usuario_registrado):
    resultado = login("joao", "Senha@123")
    return resultado


@pytest.fixture(autouse=True)
def resetar_tentativas():
    security.tentativas_login.clear()
    yield
    security.tentativas_login.clear()

def pytest_addoption(parser):
    parser.addoption(
        "--rundb",
        action="store_true",
        default=False,
        help="roda tambem os testes marcados como db"
    )

def pytest_configure(config):
    config.addinivalue_line(
        "markers", "db: marca testes que dependem do banco de dados"
    )

def pytest_collection_modifyitems(config, items):
    if config.getoption("--rundb"):
        return
    pular_db = pytest.mark.skip(reason="precisa de --rundb para rodar")
    for item in items:
        if "db" in item.keywords:
            item.add_marker(pular_db)
