import pytest
import security


def test_login_sucesso_com_stub(mocker):
    # bcrypt de verdade — gera um hash real, sem mock
    hash_valido = security.gerar_hash_senha("minhasenha123")

    # stub — controla a resposta do banco, sem bater no SQLite
    mocker.patch("security.buscar_um", return_value={
        "id": 1, "nome": "joao", "senha": hash_valido
    })

    usuario = security.login("joao", "minhasenha123")

    assert usuario.nome == "joao"


def test_login_usuario_nao_existe_com_stub(mocker):
    mocker.patch("security.buscar_um", return_value=None)

    with pytest.raises(ValueError, match="Usuário ou senha inválidos"):
        security.login("fantasma", "qualquer")


def test_login_senha_incorreta_bcrypt_real(mocker):
    # aqui é onde bcrypt de verdade importa: queremos confirmar
    # que checkpw rejeita senha errada mesmo com hash válido
    hash_valido = security.gerar_hash_senha("senhaCerta")
    mocker.patch("security.buscar_um", return_value={
        "id": 1, "nome": "joao", "senha": hash_valido
    })

    with pytest.raises(ValueError, match="inválidos"):
        security.login("joao", "senhaErrada")


def test_login_bloqueado_apos_max_tentativas(mocker):
    import dados
    mocker.patch("security.buscar_um", return_value=None)
    security.tentativas_login["joao"] = dados.MAX_TENTATIVAS_LOGIN

    with pytest.raises(Exception, match="bloqueado"):
        security.login("joao", "errada")
