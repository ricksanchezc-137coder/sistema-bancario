import bcrypt

from banco import buscar_um, executar_transacao
from dados import MAX_TENTATIVAS_LOGIN
from excecoes import ContaBloqueadaError, CredenciaisInvalidasError, UsuarioJaExisteError
from models import Usuario

# controle de tentativas em memória
tentativas_login = {}


# ------------------------
# HASH DE SENHA
# ------------------------
def gerar_hash_senha(senha: str) -> str:
    return bcrypt.hashpw(
        senha.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def verificar_senha(senha: str, hash_armazenado: str) -> bool:
    return bcrypt.checkpw(
        senha.encode("utf-8"),
        hash_armazenado.encode("utf-8")
    )


# ------------------------
# REGISTRO
# ------------------------
def registrar_usuario(nome: str, senha: str) -> None:
    hash_senha = gerar_hash_senha(senha)

    def operacao(cursor):
        cursor.execute(
            "SELECT id FROM usuarios WHERE nome = ?",
            (nome,)
        )
        if cursor.fetchone():
            raise UsuarioJaExisteError(nome)

        cursor.execute(
            "INSERT INTO usuarios(nome, senha) VALUES (?, ?)",
            (nome, hash_senha)
        )
        usuario_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO contas (usuario_id, saldo) VALUES (? , ?)",
            (usuario_id, 0)
        )

    executar_transacao(operacao)


# ------------------------
# LOGIN
# ------------------------
def login(nome: str, senha: str) -> Usuario:
    # 🔴 bloqueio por tentativas
    if tentativas_login.get(nome, 0) >= MAX_TENTATIVAS_LOGIN:
        raise ContaBloqueadaError(nome, tentativas_login[nome])

    usuario = buscar_um(
        "SELECT id, nome, senha FROM usuarios WHERE nome = ?",
        (nome,)
    )

    # 🔴 usuário não existe
    if not usuario:
        tentativas_login[nome] = tentativas_login.get(nome, 0) + 1
        raise CredenciaisInvalidasError("Usuário ou senha inválidos")

    # 🔴 senha incorreta
    if not verificar_senha(senha, usuario["senha"]):
        tentativas_login[nome] = tentativas_login.get(nome, 0) + 1
        raise CredenciaisInvalidasError("Usuário ou senha inválidos")

    # ✅ sucesso → zera tentativas
    tentativas_login[nome] = 0
    return Usuario.from_row(usuario)
