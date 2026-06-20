class Usuario:
    def __init__(self, id: int, nome: str):
        self.id = id
        self.nome = nome
        
    @classmethod
    def from_row(cls, row):
        return cls(id=row["id"], nome=row["nome"])

    def __repr__(self):
        return f"Usuario(id={self.id}, nome='{self.nome}')"


class Conta:
    def __init__(self, id: int, usuario_id: int, saldo: float):
        self.id = id
        self.usuario_id = usuario_id
        self.saldo = saldo
        
    @classmethod
    def from_row(cls, row):
        return cls(id=row["id"], usuario_id=row["usuario_id"], saldo=row["saldo"])
    
    def __repr__(self):
        return f"Conta(id={self.id}, usuario_id={self.usuario_id}, saldo={self.saldo})"