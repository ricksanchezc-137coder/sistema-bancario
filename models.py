from dataclasses import dataclass


@dataclass
class Usuario:
    id: int
    nome: str

    @classmethod
    def from_row(cls, row) -> "Usuario":
        return cls(id=row["id"], nome=row["nome"])


class Conta:
    def __init__(self, id: int, usuario_id: int, saldo: float):
        self.id = id
        self.usuario_id = usuario_id
        self.saldo = saldo

    @property
    def saldo(self) -> float:
        return self._saldo

    @saldo.setter
    def saldo(self, valor: float) -> None:
        if valor < 0:
            raise ValueError("saldo não pode ser negativo")
        self._saldo = valor

    @classmethod
    def from_row(cls, row) -> "Conta":
        return cls(id=row["id"], usuario_id=row["usuario_id"], saldo=row["saldo"])

    def __repr__(self) -> str:
        return f"Conta(id={self.id}, usuario_id={self.usuario_id}, saldo={self.saldo})"
