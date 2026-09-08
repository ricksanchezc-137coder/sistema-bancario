class ErroContaBancaria(Exception):
    """Classe base para todos os erros de dominio do sistema bancario."""


# --- autenticacao / cadastro ---
class ContaBloqueadaError(ErroContaBancaria):
    def __init__(self, nome: str, tentativas: int):
        self.nome = nome
        self.tentativas = tentativas
        super().__init__(
            f"Usuario '{nome}' bloqueado apos {tentativas} tentativas de login"
        )


class CredenciaisInvalidasError(ErroContaBancaria):
    pass


class UsuarioJaExisteError(ErroContaBancaria):
    def __init__(self, nome: str):
        self.nome = nome
        super().__init__(f"Usuario '{nome}' ja existe")


# --- operacoes financeiras ---
class ValorInvalidoError(ErroContaBancaria):
    pass


class SaldoInsuficienteError(ErroContaBancaria):
    def __init__(self, saldo: float, valor_solicitado: float):
        self.saldo = saldo
        self.valor_solicitado = valor_solicitado
        super().__init__(
            f"Saldo {saldo} insuficiente para operacao de {valor_solicitado}"
        )


class LimiteSaqueExcedidoError(ErroContaBancaria):
    def __init__(self, valor: float, limite: float):
        self.valor = valor
        self.limite = limite
        super().__init__(f"Valor {valor} excede o limite de saque de {limite}")


class ContaNaoEncontradaError(ErroContaBancaria):
    pass


class UsuarioNaoEncontradoError(ErroContaBancaria):
    pass


class TransferenciaParaSiMesmoError(ErroContaBancaria):
    pass


class InconsistenciaSaldoError(ErroContaBancaria):
    def __init__(self, saldo_tabela: float, saldo_calculado: float):
        self.saldo_tabela = saldo_tabela
        self.saldo_calculado = saldo_calculado
        super().__init__(
            f"Inconsistencia: tabela={saldo_tabela}, calculado={saldo_calculado}"
        )


class AgendamentoInvalidoError(ErroContaBancaria):
    pass
