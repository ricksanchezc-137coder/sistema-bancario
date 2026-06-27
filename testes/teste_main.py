import unittest
from unittest import mock
from main import obter_conta, menu, main


class TestObterConta(unittest.TestCase):
    """Mock de buscar_um + mock de Conta.from_row encadeados."""

    def test_retorna_conta_quando_encontrada(self):
        fake_row = {"id": 1, "usuario_id": 1, "saldo": 100.0}
        fake_conta = mock.MagicMock()

        with mock.patch("main.buscar_um", return_value=fake_row):
            with mock.patch("main.Conta.from_row", return_value=fake_conta) as mock_from_row:
                resultado = obter_conta(1)
                mock_from_row.assert_called_once_with(fake_row)
                self.assertEqual(resultado, fake_conta)

    def test_retorna_none_quando_nao_encontrada(self):
        with mock.patch("main.buscar_um", return_value=None):
            resultado = obter_conta(1)
            self.assertIsNone(resultado)


class TestMenu(unittest.TestCase):
    """side_effect como lista simula o usuário digitando em sequência."""

    def _conta_fake(self):
        conta = mock.MagicMock()
        conta.id = 1
        conta.usuario_id = 1
        conta.saldo = 500.0
        return conta

    def test_opcao_0_encerra_sem_travar(self):
        conta = self._conta_fake()
        with mock.patch("builtins.input", return_value="0"):
            with mock.patch("builtins.print"):
                menu(conta)  # se travar em loop, o teste congela

    def test_opcao_1_mostra_saldo(self):
        conta = self._conta_fake()
        nova_conta = mock.MagicMock()
        nova_conta.saldo = 750.0

        with mock.patch("builtins.input", side_effect=["1", "0"]):
            with mock.patch("main.obter_conta", return_value=nova_conta):
                with mock.patch("builtins.print") as mock_print:
                    menu(conta)
                    # assert_any_call: não importa outras chamadas ao print
                    mock_print.assert_any_call("Saldo: 750.0")

    def test_opcao_2_chama_depositar(self):
        conta = self._conta_fake()

        with mock.patch("builtins.input", side_effect=["2", "100.0", "0"]):
            with mock.patch("main.depositar") as mock_dep:
                with mock.patch("builtins.print"):
                    menu(conta)
                    mock_dep.assert_called_once_with(1, 100.0)

    def test_opcao_invalida_nao_levanta_excecao(self):
        conta = self._conta_fake()
        with mock.patch("builtins.input", side_effect=["9", "0"]):
            with mock.patch("builtins.print"):
                menu(conta)  # só verifica que não quebra


class TestMain(unittest.TestCase):
    """Testa fluxos completos da função main()."""

    def test_fluxo_registrar_usuario(self):
        # usuário escolhe "2", digita nome e senha, depois "0" pra sair
        inputs = ["2", "João", "senha123", "0"]

        with mock.patch("builtins.input", side_effect=inputs):
            with mock.patch("main.criar_tabelas"):
                with mock.patch("main.registrar_usuario") as mock_reg:
                    with mock.patch("builtins.print"):
                        main()
                        mock_reg.assert_called_once_with("João", "senha123")

    def test_fluxo_encerrar_direto(self):
        with mock.patch("builtins.input", return_value="0"):
            with mock.patch("main.criar_tabelas"):
                with mock.patch("builtins.print"):
                    main()  # deve retornar sem erro


if __name__ == "__main__":
    unittest.main(verbosity=2)
