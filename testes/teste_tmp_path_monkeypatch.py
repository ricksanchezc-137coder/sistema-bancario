import os
import pytest
import banco
from banco import criar_tabelas
import servico_v2


def _criar_conta(nome, saldo=0.0):
    """Insere usuario+conta diretamente e retorna conta_id.
    Conta sempre nasce com saldo=0 na tabela; se `saldo` > 0,
    popula pelo caminho oficial (servico_v2.depositar), que também
    grava a transação correspondente. Isso evita divergência entre
    contas.saldo e o que verificar_consistencia calcula a partir
    de transacoes, não importa como esta função seja chamada depois.
    """
    banco.executar(
        "INSERT INTO usuarios (nome, senha) VALUES (?, ?)",
        (nome, "hash_teste"),
    )
    row = banco.buscar_um("SELECT id FROM usuarios WHERE nome = ?", (nome,))
    usuario_id = row[0]

    banco.executar(
        "INSERT INTO contas (usuario_id, saldo) VALUES (?, ?)",
        (usuario_id, 0.0),
    )
    row = banco.buscar_um(
        "SELECT id FROM contas WHERE usuario_id = ?", (usuario_id,)
    )
    conta_id = row[0]

    if saldo:
        servico_v2.depositar(conta_id, saldo)

    return conta_id


def _saldo(conta_id):
    row = banco.buscar_um(
        "SELECT saldo FROM contas WHERE id = ?", (conta_id,)
    )
    return row[0] if row else None


# — 1. tmp_path cria arquivo no disco —

@pytest.mark.db
def test_banco_criado_em_tmp_path(tmp_path, monkeypatch):
    db = tmp_path / "banco.db"
    monkeypatch.setattr(banco, "DB_NAME", str(db))
    criar_tabelas()
    assert db.exists()


# — 2. depositar —

@pytest.mark.db
def test_depositar_com_tmp_path(tmp_path, monkeypatch):
    monkeypatch.setattr(banco, "DB_NAME", str(tmp_path / "banco.db"))
    criar_tabelas()
    conta_id = _criar_conta("joao")
    servico_v2.depositar(conta_id, 500.0)
    assert _saldo(conta_id) == 500.0


# — 3. sacar —

@pytest.mark.db
def test_sacar_com_tmp_path(tmp_path, monkeypatch):
    monkeypatch.setattr(banco, "DB_NAME", str(tmp_path / "banco.db"))
    criar_tabelas()
    conta_id = _criar_conta("maria")
    servico_v2.depositar(conta_id, 800.0)
    servico_v2.sacar(conta_id, 300.0)
    assert _saldo(conta_id) == 500.0


# — 4. fixture local encapsulando tmp_path + monkeypatch —

@pytest.fixture
def banco_tmp(tmp_path, monkeypatch):
    monkeypatch.setattr(banco, "DB_NAME", str(tmp_path / "banco_teste.db"))
    criar_tabelas()


@pytest.mark.db
def test_transferir_com_fixture_tmp(banco_tmp):
    conta_alice = _criar_conta("alice")
    conta_bob = _criar_conta("bob")
    servico_v2.depositar(conta_alice, 1000.0)
    servico_v2.depositar(conta_bob, 500.0)
    servico_v2.transferir(conta_alice, "bob", 200.0)
    assert _saldo(conta_alice) == 800.0
    assert _saldo(conta_bob) == 700.0


# — 5. isolamento: cada teste tem banco próprio —

@pytest.mark.db
def test_isolamento_a(tmp_path, monkeypatch):
    monkeypatch.setattr(banco, "DB_NAME", str(tmp_path / "banco.db"))
    criar_tabelas()
    conta_id = _criar_conta("carlos")
    servico_v2.depositar(conta_id, 2000.0)
    assert _saldo(conta_id) == 2000.0


@pytest.mark.db
def test_isolamento_b(tmp_path, monkeypatch):
    monkeypatch.setattr(banco, "DB_NAME", str(tmp_path / "banco.db"))
    criar_tabelas()
    # banco novo — nenhuma conta criada aqui
    assert _saldo(1) is None


# — 6. monkeypatch.setenv —

def test_monkeypatch_setenv(monkeypatch):
    monkeypatch.setenv("APP_ENV", "testing")
    assert os.environ["APP_ENV"] == "testing"