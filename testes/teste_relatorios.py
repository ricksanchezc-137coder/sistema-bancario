import unittest
from unittest import mock
from relatorios import (
    formatar_data_iso,
    buscar_nome_por_conta,
    ver_extrato,
    mostrar_extrato,
)


class TestFormatarDataIso(unittest.TestCase):
    """Função pura — sem mocks. Só entrada e saída."""

    def test_inicio_tem_hora_zero(self):
        resultado = formatar_data_iso("01/06/2024")
        self.assertEqual(resultado, "2024-06-01T00:00:00")

    def test_fim_tem_hora_23_59_59(self):
        resultado = formatar_data_iso("01/06/2024", fim=True)
        self.assertEqual(resultado, "2024-06-01T23:59:59")


class TestBuscarNomePorConta(unittest.TestCase):
    """Mock de função importada: relatorios.buscar_um"""

    def test_retorna_nome_do_usuario(self):
        with mock.patch("relatorios.buscar_um") as mock_buscar:
            mock_buscar.return_value = {"nome": "João"}
            resultado = buscar_nome_por_conta(1)
            self.assertEqual(resultado, "João")

    def test_retorna_desconhecido_quando_sem_resultado(self):
        with mock.patch("relatorios.buscar_um") as mock_buscar:
            mock_buscar.return_value = None
            resultado = buscar_nome_por_conta(1)
            self.assertEqual(resultado, "Desconhecido")

    def test_passa_conta_id_correto(self):
        with mock.patch("relatorios.buscar_um") as mock_buscar:
            mock_buscar.return_value = {"nome": "Maria"}
            buscar_nome_por_conta(42)
            # mock.ANY aceita qualquer valor — útil pra ignorar a query SQL
            mock_buscar.assert_called_once_with(mock.ANY, (42,))


class TestVerExtrato(unittest.TestCase):
    """Mock de buscar_todos — return_value como lista fake."""

    def test_retorna_lista_de_transacoes(self):
        fake_lista = [{"tipo": "deposito", "valor": 100.0}]
        with mock.patch("relatorios.buscar_todos") as mock_buscar:
            mock_buscar.return_value = fake_lista
            resultado = ver_extrato(1)
            self.assertEqual(resultado, fake_lista)

    def test_chama_buscar_todos_uma_vez(self):
        with mock.patch("relatorios.buscar_todos") as mock_buscar:
            mock_buscar.return_value = []
            ver_extrato(1)
            mock_buscar.assert_called_once()


class TestMostrarExtrato(unittest.TestCase):
    """Mock de função do próprio módulo + mock de builtins.print."""

    def test_sem_transacoes_imprime_aviso(self):
        with mock.patch("relatorios.ver_extrato") as mock_extrato:
            mock_extrato.return_value = []
            with mock.patch("builtins.print") as mock_print:
                mostrar_extrato(1)
                mock_print.assert_called_once_with(
                    "Nenhuma transação encontrada."
                )

    def test_com_transacoes_imprime_cabecalho_e_linha(self):
        fake_transacoes = [{"tipo": "qualquer"}]
        with mock.patch("relatorios.ver_extrato") as mock_extrato:
            mock_extrato.return_value = fake_transacoes
            # mockamos formatar_transacao pra não precisar montar
            # uma transação com todos os campos reais
            with mock.patch("relatorios.formatar_transacao") as mock_fmt:
                mock_fmt.return_value = "linha formatada"
                with mock.patch("builtins.print") as mock_print:
                    mostrar_extrato(1)
                    # print foi chamado pra o cabeçalho + 1 linha
                    self.assertEqual(mock_print.call_count, 2)
                    mock_fmt.assert_called_once()


if __name__ == "__main__":
    unittest.main(verbosity=2)
