from datetime import date, datetime

from banco import buscar_todos, buscar_um, executar, executar_transacao
import dados
from dados import (
    LIMITE_SAQUE,
    TIPO_DEPOSITO,
    TIPO_SAQUE,
    TIPO_TRANSFERENCIA_ENVIADA,
    TIPO_TRANSFERENCIA_RECEBIDA,
)
from excecoes import (
    AgendamentoInvalidoError,
    ContaNaoEncontradaError,
    InconsistenciaSaldoError,
    LimiteSaqueExcedidoError,
    SaldoInsuficienteError,
    TransferenciaParaSiMesmoError,
    UsuarioNaoEncontradoError,
    ValorInvalidoError,
)
from models import Conta


# ------------------------
# VALIDAÇÕES
# ------------------------
def validar_valor(valor: float) -> None:
    if valor <= 0:
        raise ValorInvalidoError("Valor inválido")


def validar_saque(saldo: float, valor: float) -> float:
    if valor > saldo:
        raise SaldoInsuficienteError(saldo, valor)
    if valor > LIMITE_SAQUE:
        raise LimiteSaqueExcedidoError(valor, LIMITE_SAQUE)
    return saldo - valor


def obter_conta(cursor, conta_id: int, contexto: str = "Conta") -> Conta:
    cursor.execute(
        "SELECT id, usuario_id, saldo FROM contas WHERE id = ?",
        (conta_id,)
    )
    conta = cursor.fetchone()
    if not conta:
        raise ContaNaoEncontradaError(f"{contexto} não encontrada")
    return Conta.from_row(conta)


# ------------------------
# CONSISTÊNCIA
# ------------------------
def calcular_saldo(cursor, conta_id: int) -> float:
    cursor.execute("""
        SELECT tipo, conta_origem_id, conta_destino_id, valor
        FROM transacoes
        WHERE conta_origem_id = ? OR conta_destino_id = ?
    """, (conta_id, conta_id))

    saldo = 0
    for t in cursor.fetchall():
        tipo = t["tipo"]
        valor = t["valor"]
        match tipo:
            case dados.TIPO_DEPOSITO:
                saldo += valor
            case dados.TIPO_SAQUE:
                saldo -= valor
            case dados.TIPO_TRANSFERENCIA_ENVIADA if t["conta_origem_id"] == conta_id:
                saldo -= valor
            case dados.TIPO_TRANSFERENCIA_RECEBIDA if t["conta_destino_id"] == conta_id:
                saldo += valor
    return saldo


def verificar_consistencia(cursor, conta_id: int) -> None:
    conta = obter_conta(cursor, conta_id)
    saldo_tabela = conta.saldo
    saldo_calculado = calcular_saldo(cursor, conta_id)
    if abs(saldo_tabela - saldo_calculado) > 0.01:
        raise InconsistenciaSaldoError(saldo_tabela, saldo_calculado)


# ------------------------
# OPERAÇÕES
# ------------------------
def depositar(conta_id: int, valor: float, agora: datetime = None) -> None:
    validar_valor(valor)
    agora = agora or datetime.now()

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
        """, (TIPO_DEPOSITO, conta.id, valor, novo_saldo, agora.isoformat()))
        verificar_consistencia(cursor, conta_id)

    executar_transacao(operacao)


def sacar(conta_id: int, valor: float, agora: datetime = None) -> None:
    validar_valor(valor)
    agora = agora or datetime.now()

    def operacao(cursor):
        conta = obter_conta(cursor, conta_id)
        novo_saldo = validar_saque(conta.saldo, valor)
        cursor.execute(
            "UPDATE contas SET saldo = ? WHERE id = ?",
            (novo_saldo, conta.id)
        )
        cursor.execute("""
            INSERT INTO transacoes(tipo, conta_origem_id, valor, saldo_apos, data_hora)
            VALUES(?, ?, ?, ?, ?)
        """, (TIPO_SAQUE, conta.id, valor, novo_saldo, agora.isoformat()))
        verificar_consistencia(cursor, conta_id)

    executar_transacao(operacao)


def transferir(origem_id: int, destino_nome: str, valor: float, agora: datetime = None) -> None:
    validar_valor(valor)
    agora = agora or datetime.now()

    def operacao(cursor):
        conta_origem = obter_conta(cursor, origem_id, contexto="Conta de origem")
        if valor > conta_origem.saldo:
            raise SaldoInsuficienteError(conta_origem.saldo, valor)

        cursor.execute(
            "SELECT id FROM usuarios WHERE nome = ?",
            (destino_nome,)
        )
        usuario = cursor.fetchone()
        if not usuario:
            raise UsuarioNaoEncontradoError("Usuário de destino não encontrado")

        cursor.execute(
            "SELECT id, usuario_id, saldo FROM contas WHERE usuario_id = ?",
            (usuario["id"],)
        )
        conta_destino_row = cursor.fetchone()
        if not conta_destino_row:
            raise ContaNaoEncontradaError("Conta de destino não encontrada")
        conta_destino = Conta.from_row(conta_destino_row)

        if conta_destino.id == origem_id:
            raise TransferenciaParaSiMesmoError("Transferência para si mesmo")

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

        data_hora = agora.isoformat()
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


def resolver_conta_destino(destino_nome: str) -> int:
    usuario = buscar_um(
        "SELECT id FROM usuarios WHERE nome = ?",
        (destino_nome,)
    )
    if not usuario:
        raise UsuarioNaoEncontradoError("Usuário de destino não encontrado")

    conta_destino_row = buscar_um(
        "SELECT id FROM contas WHERE usuario_id = ?",
        (usuario["id"],)
    )
    if not conta_destino_row:
        raise ContaNaoEncontradaError("Conta de destino não encontrada")

    return conta_destino_row["id"]


def agendar_transferencia(origem_id: int, destino_nome: str, valor: float, data_agendada: date) -> None:
    if data_agendada < date.today():
        raise AgendamentoInvalidoError("Nao e possivel agendar para data passada")

    conta_destino_id = resolver_conta_destino(destino_nome)

    executar(
        """
        INSERT INTO transferencias_agendadas
        (conta_origem_id, conta_destino_id, valor, data_agendada, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        (origem_id, conta_destino_id, valor, data_agendada.isoformat(), "pendente")
    )


def executar_transferencias_vencidas(hoje: date = None) -> None:
    hoje = hoje or date.today()
    vencidas = buscar_todos(
        "SELECT * FROM transferencias_agendadas WHERE status = 'pendente' AND data_agendada <= ?",
        (hoje,)
    )
    for transferencia in vencidas:
        def operacao(cursor, transferencia=transferencia):
            cursor.execute(
                "UPDATE contas SET saldo = saldo - ? WHERE id = ?",
                (transferencia['valor'], transferencia['conta_origem_id'])
            )
            cursor.execute(
                "UPDATE contas SET saldo = saldo + ? WHERE id = ?",
                (transferencia['valor'], transferencia['conta_destino_id'])
            )
            cursor.execute(
                "UPDATE transferencias_agendadas SET status = 'executada' WHERE id = ?",
                (transferencia['id'],)
            )
        executar_transacao(operacao)
