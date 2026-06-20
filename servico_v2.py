from banco import buscar_um, executar_transacao
from dados import LIMITE_SAQUE, TIPO_DEPOSITO, TIPO_SAQUE, TIPO_TRANSFERENCIA_ENVIADA, TIPO_TRANSFERENCIA_RECEBIDA
from models import Conta
from datetime import datetime

# ------------------------
# VALIDAÇÕES
# ------------------------

def validar_valor(valor: float):
    if valor <= 0:
        raise ValueError("Valor inválido")


def obter_conta(cursor, conta_id: int):
    cursor.execute(
        "SELECT id, usuario_id, saldo FROM contas WHERE id = ?",
        (conta_id,)
    )
    conta = cursor.fetchone()

    if not conta:
        raise ValueError("Conta não encontrada")

    return Conta.from_row(conta)


# ------------------------
# CONSISTÊNCIA
# ------------------------

def calcular_saldo(cursor, conta_id: int):
    cursor.execute("""
        SELECT tipo, conta_origem_id, conta_destino_id, valor
        FROM transacoes
        WHERE conta_origem_id = ? OR conta_destino_id = ?
    """, (conta_id, conta_id))

    saldo = 0

    for t in cursor.fetchall():
        tipo = t["tipo"]
        valor = t["valor"]

        if tipo == TIPO_DEPOSITO:
            saldo += valor
        elif tipo == TIPO_SAQUE:
            saldo -= valor
        elif tipo == TIPO_TRANSFERENCIA_ENVIADA:
            if t["conta_origem_id"] == conta_id:
                saldo -= valor
        elif tipo == TIPO_TRANSFERENCIA_RECEBIDA:
            if t["conta_destino_id"] == conta_id:
                saldo += valor

    return saldo


def verificar_consistencia(cursor, conta_id: int):
    conta = obter_conta(cursor, conta_id)

    saldo_tabela = conta.saldo
    saldo_calculado = calcular_saldo(cursor, conta_id)

    if abs(saldo_tabela - saldo_calculado) > 0.01:
        raise Exception(
            f"Inconsistência: tabela={saldo_tabela}, calculado={saldo_calculado}"
        )


# ------------------------
# OPERAÇÕES
# ------------------------

def depositar(conta_id: int, valor: float):
    validar_valor(valor)

    def operacao(cursor):
        conta = obter_conta(cursor, conta_id)
        novo_saldo = conta.saldo + valor

        cursor.execute(
            "UPDATE contas SET saldo = ? WHERE id = ?",
            (novo_saldo, conta.id)
        )

        cursor.execute("""
            INSERT INTO transacoes(tipo, conta_destino_id, valor, saldo_apos, data_hora)
            VALUES(?, ?, ?, ?, ?)
        """, (TIPO_DEPOSITO, conta.id, valor, novo_saldo, datetime.now().isoformat()))

        verificar_consistencia(cursor, conta_id)

    executar_transacao(operacao)


def sacar(conta_id: int, valor: float):
    validar_valor(valor)

    def operacao(cursor):
        conta = obter_conta(cursor, conta_id)

        if valor > conta.saldo:
            raise ValueError("Saldo insuficiente")
        if valor > LIMITE_SAQUE:
            raise ValueError("Limite de saque excedido")

        novo_saldo = conta.saldo - valor

        cursor.execute(
            "UPDATE contas SET saldo = ? WHERE id = ?",
            (novo_saldo, conta.id)
        )

        cursor.execute("""
            INSERT INTO transacoes(tipo, conta_origem_id, valor, saldo_apos, data_hora)
            VALUES(?, ?, ?, ?, ?)
        """, (TIPO_SAQUE, conta.id, valor, novo_saldo, datetime.now().isoformat()))

        verificar_consistencia(cursor, conta_id)

    executar_transacao(operacao)


def transferir(origem_id: int, destino_nome: str, valor: float):
    validar_valor(valor)

    def operacao(cursor):
        conta_origem = obter_conta(cursor, origem_id)

        if valor > conta_origem.saldo:
            raise ValueError("Saldo insuficiente")

        cursor.execute(
            "SELECT id FROM usuarios WHERE nome = ?",
            (destino_nome,)
        )
        usuario = cursor.fetchone()

        if not usuario:
            raise ValueError("Usuário de destino não encontrado")

        cursor.execute(
            "SELECT id, usuario_id, saldo FROM contas WHERE usuario_id = ?",
            (usuario["id"],)
        )
        conta_destino_row = cursor.fetchone()

        if not conta_destino_row:
            raise ValueError("Conta de destino não encontrada")

        conta_destino = Conta.from_row(conta_destino_row)

        if conta_destino.id == origem_id:
            raise ValueError("Transferência para si mesmo")

        novo_saldo_origem = conta_origem.saldo - valor
        novo_saldo_destino = conta_destino.saldo + valor

        cursor.execute(
            "UPDATE contas SET saldo = ? WHERE id = ?",
            (novo_saldo_origem, origem_id)
        )
        cursor.execute(
            "UPDATE contas SET saldo = ? WHERE id = ?",
            (novo_saldo_destino, conta_destino.id)
        )

        data_hora = datetime.now().isoformat()

        cursor.execute("""
            INSERT INTO transacoes(tipo, conta_origem_id, conta_destino_id, valor, saldo_apos, data_hora)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (TIPO_TRANSFERENCIA_ENVIADA, origem_id, conta_destino.id, valor, novo_saldo_origem, data_hora))

        cursor.execute("""
            INSERT INTO transacoes(tipo, conta_origem_id, conta_destino_id, valor, saldo_apos, data_hora)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (TIPO_TRANSFERENCIA_RECEBIDA, origem_id, conta_destino.id, valor, novo_saldo_destino, data_hora))

        verificar_consistencia(cursor, origem_id)
        verificar_consistencia(cursor, conta_destino.id)

    executar_transacao(operacao)










