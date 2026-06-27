import unittest
from models import Usuario, Conta


class TestUsuario(unittest.TestCase):
    def setUp(self):
        self.usuario = Usuario(id=1, nome="João")

    def test_init_define_atributos(self):
        self.assertEqual(self.usuario.id, 1)
        self.assertEqual(self.usuario.nome, "João")

    def test_from_row_cria_usuario_correto(self):
        row = {"id": 2, "nome": "Maria"}
        usuario = Usuario.from_row(row)
        self.assertEqual(usuario.id, 2)
        self.assertEqual(usuario.nome, "Maria")

    def test_repr_formato_correto(self):
        esperado = "Usuario(id=1, nome='João')"
        self.assertEqual(repr(self.usuario), esperado)


class TestConta(unittest.TestCase):
    def setUp(self):
        self.conta = Conta(id=1, usuario_id=1, saldo=100.0)

    def test_init_define_atributos(self):
        self.assertEqual(self.conta.id, 1)
        self.assertEqual(self.conta.usuario_id, 1)
        self.assertEqual(self.conta.saldo, 100.0)

    def test_from_row_cria_conta_correta(self):
        row = {"id": 3, "usuario_id": 2, "saldo": 250.50}
        conta = Conta.from_row(row)
        self.assertEqual(conta.id, 3)
        self.assertEqual(conta.usuario_id, 2)
        self.assertEqual(conta.saldo, 250.50)

    def test_repr_formato_correto(self):
        esperado = "Conta(id=1, usuario_id=1, saldo=100.0)"
        self.assertEqual(repr(self.conta), esperado)


if __name__ == "__main__":
    unittest.main()
