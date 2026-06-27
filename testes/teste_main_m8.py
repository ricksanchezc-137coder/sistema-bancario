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

    def _conta_fake(self):
        conta = mock.MagicMock()
        conta.id = 1
        conta.usuario_id = 1
        conta.saldo = 500.0
        return conta

    # ── Módulo 6 ──────────────────────────────────────────────────────

    def test_opcao_0_encerra_sem_travar(self):
        conta = self._conta_fake()
        with mock.patch("builtins.input", return_value="0"):
            with mock.patch("builtins.print"):
                menu(conta)

    def test_opcao_1_mostra_saldo(self):
        conta = self._conta_fake()
        nova_conta = mock.MagicMock()
        nova_conta.saldo = 750.0

        with mock.patch("builtins.input", side_effect=["1", "0"]):
            with mock.patch("main.obter_conta", return_value=nova_conta):
                with mock.patch("builtins.print") as mock_print:
                    menu(conta)
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
                menu(conta)

    # ── Módulo 9 ──────────────────────────────────────────────────────

    def test_opcao_3_chama_sacar(self):
        conta = self._conta_fake()
        with mock.patch("builtins.input", side_effect=["3", "50.0", "0"]):
            with mock.patch("main.sacar") as mock_sac:
                with mock.patch("builtins.print"):
                    menu(conta)
                    mock_sac.assert_called_once_with(1, 50.0)

    def test_opcao_4_chama_transferir(self):
        conta = self._conta_fake()
        with mock.patch("builtins.input", side_effect=["4", "maria", "200.0", "0"]):
            with mock.patch("main.transferir") as mock_trans:
                with mock.patch("builtins.print"):
                    menu(conta)
                    mock_trans.assert_called_once_with(1, "maria", 200.0)

    def test_opcao_5_1_chama_mostrar_extrato(self):
        conta = self._conta_fake()
        with mock.patch("builtins.input", side_effect=["5", "1", "0"]):
            with mock.patch("main.mostrar_extrato") as mock_ext:
                with mock.patch("builtins.print"):
                    menu(conta)
                    mock_ext.assert_called_once_with(1)

    def test_opcao_5_2_chama_mostrar_extrato_periodo(self):
        conta = self._conta_fake()
        with mock.patch("builtins.input", side_effect=["5", "2", "0"]):
            with mock.patch("main.mostrar_extrato_periodo") as mock_ext:
                with mock.patch("builtins.print"):
                    menu(conta)
                    mock_ext.assert_called_once_with(1)

    def test_opcao_5_3_extrato_rapido_hoje(self):
        conta = self._conta_fake()
        with mock.patch("builtins.input", side_effect=["5", "3", "1", "0"]):
            with mock.patch("main.mostrar_extrato_rapido") as mock_rap:
                with mock.patch("builtins.print"):
                    menu(conta)
                    mock_rap.assert_called_once_with(1, 1)

    def test_opcao_5_3_extrato_rapido_7_dias(self):
        conta = self._conta_fake()
        with mock.patch("builtins.input", side_effect=["5", "3", "2", "0"]):
            with mock.patch("main.mostrar_extrato_rapido") as mock_rap:
                with mock.patch("builtins.print"):
                    menu(conta)
                    mock_rap.assert_called_once_with(1, 7)

    def test_opcao_5_3_extrato_rapido_30_dias(self):
        conta = self._conta_fake()
        with mock.patch("builtins.input", side_effect=["5", "3", "3", "0"]):
            with mock.patch("main.mostrar_extrato_rapido") as mock_rap:
                with mock.patch("builtins.print"):
                    menu(conta)
                    mock_rap.assert_called_once_with(1, 30)

    def test_opcao_5_3_invalido(self):
        conta = self._conta_fake()
        with mock.patch("builtins.input", side_effect=["5", "3", "9", "0"]):
            with mock.patch("builtins.print") as mock_print:
                menu(conta)
                mock_print.assert_any_call("Opcao invalida")

    def test_opcao_5_4_exportar_extrato(self):
        conta = self._conta_fake()
        with mock.patch("builtins.input", side_effect=["5", "4", "0"]):
            with mock.patch("main.exportar_extrato") as mock_exp:
                with mock.patch("builtins.print"):
                    menu(conta)
                    mock_exp.assert_called_once_with(1)

    def test_opcao_5_5_exportar_extrato_periodo(self):
        conta = self._conta_fake()
        with mock.patch("builtins.input", side_effect=["5", "5", "0"]):
            with mock.patch("main.exportar_extrato_periodo") as mock_exp:
                with mock.patch("builtins.print"):
                    menu(conta)
                    mock_exp.assert_called_once_with(1)

    def test_opcao_5_6_exportar_csv(self):
        conta = self._conta_fake()
        with mock.patch("builtins.input", side_effect=["5", "6", "0"]):
            with mock.patch("main.exportar_csv") as mock_csv:
                with mock.patch("builtins.print"):
                    menu(conta)
                    mock_csv.assert_called_once_with(1)

    def test_opcao_5_invalido(self):
        conta = self._conta_fake()
        with mock.patch("builtins.input", side_effect=["5", "9", "0"]):
            with mock.patch("builtins.print") as mock_print:
                menu(conta)
                mock_print.assert_any_call("Opcao Invalida")

    def test_valor_invalido_capturado(self):
        """float("abc") levanta ValueError → capturado → menu continua."""
        conta = self._conta_fake()
        with mock.patch("builtins.input", side_effect=["2", "abc", "0"]):
            with mock.patch("builtins.print") as mock_print:
                menu(conta)
                todas = [str(c) for c in mock_print.call_args_list]
                self.assertTrue(any("Erro:" in c for c in todas))


class TestMain(unittest.TestCase):

    # ── Módulo 6 ──────────────────────────────────────────────────────

    def test_fluxo_registrar_usuario(self):
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
                    main()

    # ── Módulo 9 ──────────────────────────────────────────────────────

    def test_registrar_usuario_valor_invalido(self):
        inputs = ["2", "joao", "senha123", "0"]

        with mock.patch("builtins.input", side_effect=inputs):
            with mock.patch("main.criar_tabelas"):
                with mock.patch(
                    "main.registrar_usuario",
                    side_effect=ValueError("Usuário já existe")
                ):
                    with mock.patch("builtins.print") as mock_print:
                        main()
                        mock_print.assert_any_call("Erro: Usuário já existe")

    def test_opcao_invalida_main(self):
        inputs = ["9", "0"]
        with mock.patch("builtins.input", side_effect=inputs):
            with mock.patch("main.criar_tabelas"):
                with mock.patch("builtins.print") as mock_print:
                    main()
                    mock_print.assert_any_call("Opcao invalida")

    def test_fluxo_login_sucesso_chama_menu(self):
        """Login bem-sucedido deve chamar menu() com a conta correta."""
        usuario_fake = mock.MagicMock()
        usuario_fake.id = 1
        conta_fake = mock.MagicMock()

        # "1"=escolha login, "joao"=nome, "senha123"=senha, "0"=sair do main
        inputs = ["1", "joao", "senha123", "0"]

        with mock.patch("builtins.input", side_effect=inputs):
            with mock.patch("main.criar_tabelas"):
                with mock.patch("main.login", return_value=usuario_fake):
                    with mock.patch("main.obter_conta", return_value=conta_fake):
                        with mock.patch("main.menu") as mock_menu:
                            with mock.patch("builtins.print"):
                                main()
                                mock_menu.assert_called_once_with(conta_fake)

    def test_fluxo_login_erro_tenta_novamente(self):
        """ValueError no login: exibe erro e repete o loop."""
        usuario_fake = mock.MagicMock()
        usuario_fake.id = 1
        conta_fake = mock.MagicMock()

        # 1ª tentativa falha, 2ª tem sucesso
        inputs = ["1", "joao", "errada", "joao", "certa", "0"]

        with mock.patch("builtins.input", side_effect=inputs):
            with mock.patch("main.criar_tabelas"):
                with mock.patch(
                    "main.login",
                    side_effect=[ValueError("Senha incorreta"), usuario_fake]
                ):
                    with mock.patch("main.obter_conta", return_value=conta_fake):
                        with mock.patch("main.menu"):
                            with mock.patch("builtins.print") as mock_print:
                                main()
                                mock_print.assert_any_call("Erro: Senha incorreta")

    def test_fluxo_login_conta_nao_encontrada(self):
        """Login OK mas sem conta: exibe mensagem e sai."""
        usuario_fake = mock.MagicMock()
        usuario_fake.id = 1

        # Após "Conta não encontrada", main() dá return — não precisa de "0"
        inputs = ["1", "joao", "senha123"]

        with mock.patch("builtins.input", side_effect=inputs):
            with mock.patch("main.criar_tabelas"):
                with mock.patch("main.login", return_value=usuario_fake):
                    with mock.patch("main.obter_conta", return_value=None):
                        with mock.patch("builtins.print") as mock_print:
                            main()
                            mock_print.assert_any_call("Conta não encontrada")


    def test_login_excecao_generica(self):
        inputs = ["1", "joao", "senha123", "0"]
        with mock.patch("builtins.input", side_effect=inputs):
            with mock.patch("main.criar_tabelas"):
                with mock.patch(
                    "main.login",
                    side_effect=Exception("Erro inesperado")
                ):
                    with mock.patch("builtins.print") as mock_print:
                        main()
                        mock_print.assert_any_call("Erro: Erro inesperado")


if __name__ == "__main__":
    unittest.main(verbosity=2)
