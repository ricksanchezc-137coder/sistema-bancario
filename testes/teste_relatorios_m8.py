from datetime import datetime, timedelta
import unittest
import os
import csv
import tempfile
from unittest.mock import patch
from dados import (
    TIPO_DEPOSITO,
    TIPO_SAQUE,
    TIPO_TRANSFERENCIA_ENVIADA,
    TIPO_TRANSFERENCIA_RECEBIDA,
)
from relatorios import (
    formatar_data_iso,
    formatar_transacao,
    ver_extrato,
    ver_extrato_periodo,
    exportar_csv,
    mostrar_extrato,
    buscar_nome_por_conta,
    mostrar_extrato_periodo,   # novo
    mostrar_extrato_rapido,    # novo
    exportar_extrato,          # novo
    exportar_extrato_periodo
)


# ─── Helper ───────────────────────────────────────
def make_transacao(tipo, valor=100.0, saldo_apos=500.0,
                   data_hora="2024-01-15T10:30:00",
                   conta_origem_id=1, conta_destino_id=2):
    return {
        "tipo": tipo,
        "valor": valor,
        "saldo_apos": saldo_apos,
        "data_hora": data_hora,
        "conta_origem_id": conta_origem_id,
        "conta_destino_id": conta_destino_id,
    }


# ─── 1. Função pura — sem mocks ───────────────────
class TestFormatarDataIso(unittest.TestCase):

    def test_inicio_do_dia(self):
        resultado = formatar_data_iso("15/01/2024")
        self.assertEqual(resultado, "2024-01-15T00:00:00")

    def test_fim_do_dia(self):
        resultado = formatar_data_iso("15/01/2024", fim=True)
        self.assertEqual(resultado, "2024-01-15T23:59:59")

    def test_formato_invalido_levanta_excecao(self):
        with self.assertRaises(ValueError):
            formatar_data_iso("2024-01-15")  # formato errado


# ─── 2. formatar_transacao ────────────────────────
class TestFormatarTransacao(unittest.TestCase):

    def test_deposito(self):
        t = make_transacao(TIPO_DEPOSITO, valor=100.0, saldo_apos=600.0)
        resultado = formatar_transacao(t, 1)
        self.assertIn("+ R$100.00", resultado)
        self.assertIn("Depósito", resultado)
        self.assertIn("Saldo: R$600.00", resultado)

    def test_saque(self):
        t = make_transacao(TIPO_SAQUE, valor=50.0, saldo_apos=450.0)
        resultado = formatar_transacao(t, 1)
        self.assertIn("- R$50.00", resultado)
        self.assertIn("Saque", resultado)
        self.assertIn("Saldo: R$450.00", resultado)

    @patch("relatorios.buscar_nome_por_conta")
    def test_transferencia_enviada(self, mock_nome):
        mock_nome.return_value = "Maria"
        t = make_transacao(
            TIPO_TRANSFERENCIA_ENVIADA,
            valor=200.0, saldo_apos=300.0,
            conta_destino_id=2
        )
        resultado = formatar_transacao(t, 1)
        self.assertIn("- R$200.00", resultado)
        self.assertIn("Enviado para Maria", resultado)
        mock_nome.assert_called_once_with(2)

    @patch("relatorios.buscar_nome_por_conta")
    def test_transferencia_recebida(self, mock_nome):
        mock_nome.return_value = "Carlos"
        t = make_transacao(
            TIPO_TRANSFERENCIA_RECEBIDA,
            valor=150.0, saldo_apos=650.0,
            conta_origem_id=3
        )
        resultado = formatar_transacao(t, 2)
        self.assertIn("+ R$150.00", resultado)
        self.assertIn("Recebido de Carlos", resultado)
        mock_nome.assert_called_once_with(3)

    def test_tipo_desconhecido(self):
        t = make_transacao("tipo_invalido")
        resultado = formatar_transacao(t, 1)
        self.assertEqual(resultado, "Transação desconhecida")


# ─── 3. buscar_nome_por_conta ─────────────────────
class TestBuscarNomePorConta(unittest.TestCase):

    @patch("relatorios.buscar_um")
    def test_nome_encontrado(self, mock_buscar):
        mock_buscar.return_value = {"nome": "Ana"}
        self.assertEqual(buscar_nome_por_conta(5), "Ana")

    @patch("relatorios.buscar_um")
    def test_conta_nao_encontrada(self, mock_buscar):
        mock_buscar.return_value = None
        self.assertEqual(buscar_nome_por_conta(99), "Desconhecido")


# ─── 4. ver_extrato ───────────────────────────────
class TestVerExtrato(unittest.TestCase):

    @patch("relatorios.buscar_todos")
    def test_retorna_transacoes(self, mock_buscar):
        fake = [make_transacao(TIPO_DEPOSITO), make_transacao(TIPO_SAQUE)]
        mock_buscar.return_value = fake
        resultado = ver_extrato(1)
        self.assertEqual(resultado, fake)
        mock_buscar.assert_called_once()

    @patch("relatorios.buscar_todos")
    def test_retorna_lista_vazia(self, mock_buscar):
        mock_buscar.return_value = []
        self.assertEqual(ver_extrato(1), [])


# ─── 5. ver_extrato_periodo ───────────────────────
class TestVerExtratoPeriodo(unittest.TestCase):

    @patch("relatorios.buscar_todos")
    def test_retorna_transacoes_no_periodo(self, mock_buscar):
        fake = [make_transacao(TIPO_DEPOSITO)]
        mock_buscar.return_value = fake
        resultado = ver_extrato_periodo(
            1,
            "2024-01-01T00:00:00",
            "2024-01-31T23:59:59"
        )
        self.assertEqual(resultado, fake)
        mock_buscar.assert_called_once()

    @patch("relatorios.buscar_todos")
    def test_retorna_vazio_fora_do_periodo(self, mock_buscar):
        mock_buscar.return_value = []
        resultado = ver_extrato_periodo(
            1,
            "2024-01-01T00:00:00",
            "2024-01-31T23:59:59"
        )
        self.assertEqual(resultado, [])


# ─── 6. mostrar_extrato ───────────────────────────
class TestMostrarExtrato(unittest.TestCase):

    @patch("builtins.print")
    @patch("relatorios.ver_extrato")
    def test_sem_transacoes(self, mock_ver, mock_print):
        mock_ver.return_value = []
        mostrar_extrato(1)
        mock_print.assert_called_with("Nenhuma transação encontrada.")

    @patch("builtins.print")
    @patch("relatorios.ver_extrato")
    def test_com_transacoes_imprime_extrato(self, mock_ver, mock_print):
        t = make_transacao(TIPO_DEPOSITO, valor=100.0, saldo_apos=600.0)
        mock_ver.return_value = [t]
        mostrar_extrato(1)
        args_impressos = [
            args[0]
            for args, _ in mock_print.call_args_list
            if args
        ]
        self.assertTrue(any("EXTRATO" in str(a) for a in args_impressos))
        self.assertTrue(any("Depósito" in str(a) for a in args_impressos))


# ─── 7. exportar_csv — arquivo real ──────────────
class TestExportarCsv(unittest.TestCase):

    @patch("relatorios.buscar_todos")
    @patch("builtins.print")
    def test_cria_csv_com_cabecalho_e_linha(self, mock_print, mock_buscar):
        mock_buscar.return_value = [{
            "data_hora": "2024-01-15T10:30:00",
            "tipo": TIPO_DEPOSITO,
            "valor": 100.0,
            "saldo_apos": 600.0,
        }]
        pasta_original = os.getcwd()
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            try:
                exportar_csv(1)
                with open("extrato.csv", encoding="utf-8") as f:
                    linhas = list(csv.reader(f))
            finally:
                os.chdir(pasta_original)

        self.assertEqual(linhas[0], ["data", "tipo", "valor", "saldo_apos"])
        self.assertEqual(linhas[1][1], TIPO_DEPOSITO)
        mock_print.assert_called_with("Extrato exportado.")

    @patch("relatorios.buscar_todos")
    @patch("builtins.print")
    def test_sem_transacoes_apenas_cabecalho(self, mock_print, mock_buscar):
        mock_buscar.return_value = []
        pasta_original = os.getcwd()
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            try:
                exportar_csv(1)
                with open("extrato.csv", encoding="utf-8") as f:
                    linhas = list(csv.reader(f))
            finally:
                os.chdir(pasta_original)

        self.assertEqual(len(linhas), 1)
        self.assertEqual(linhas[0], ["data", "tipo", "valor", "saldo_apos"])
# ─── 8. mostrar_extrato_periodo ───────────────────
class TestMostrarExtratoPeriodo(unittest.TestCase):

    @patch("builtins.print")
    @patch("relatorios.ver_extrato_periodo")
    @patch("builtins.input")
    def test_sem_transacoes(self, mock_input, mock_ver, mock_print):
        mock_input.side_effect = ["15/01/2024", "31/01/2024"]
        mock_ver.return_value = []
        mostrar_extrato_periodo(1)
        mock_print.assert_called_with("Nenhuma transação no período.")

    @patch("builtins.print")
    @patch("relatorios.ver_extrato_periodo")
    @patch("builtins.input")
    def test_imprime_cabecalho(self, mock_input, mock_ver, mock_print):
        mock_input.side_effect = ["15/01/2024", "31/01/2024"]
        t = make_transacao(TIPO_DEPOSITO, valor=100.0, saldo_apos=600.0)
        mock_ver.return_value = [t]
        mostrar_extrato_periodo(1)
        args = [a[0] for a, _ in mock_print.call_args_list if a]
        self.assertTrue(any("EXTRATO POR PERÍODO" in str(a) for a in args))

    @patch("builtins.print")
    @patch("relatorios.ver_extrato_periodo")
    @patch("builtins.input")
    def test_passa_datas_corretas(self, mock_input, mock_ver, mock_print):
        mock_input.side_effect = ["15/01/2024", "31/01/2024"]
        mock_ver.return_value = []
        mostrar_extrato_periodo(1)
        mock_ver.assert_called_once_with(
            1,
            "2024-01-15T00:00:00",
            "2024-01-31T23:59:59"
        )


# ─── 9. mostrar_extrato_rapido ────────────────────
class TestMostrarExtratoRapido(unittest.TestCase):

    @patch("builtins.print")
    @patch("relatorios.ver_extrato_periodo")
    @patch("relatorios.datetime")
    def test_sem_transacoes(self, mock_dt, mock_ver, mock_print):
        mock_dt.now.return_value = datetime(2024, 1, 15, 10, 30)
        mock_ver.return_value = []
        mostrar_extrato_rapido(1, 7)
        mock_print.assert_called_with("Nenhuma transação encontrada.")

    @patch("builtins.print")
    @patch("relatorios.ver_extrato_periodo")
    @patch("relatorios.datetime")
    def test_imprime_titulo_com_dias(self, mock_dt, mock_ver, mock_print):
        fake_agora = datetime(2024, 1, 15, 10, 30)
        mock_dt.now.return_value = fake_agora
        mock_dt.fromisoformat.side_effect = datetime.fromisoformat
        t = make_transacao(TIPO_DEPOSITO, valor=100.0, saldo_apos=600.0)
        mock_ver.return_value = [t]
        mostrar_extrato_rapido(1, 30)
        args = [a[0] for a, _ in mock_print.call_args_list if a]
        self.assertTrue(any("ÚLTIMOS 30 DIAS" in str(a) for a in args))

    @patch("builtins.print")
    @patch("relatorios.ver_extrato_periodo")
    @patch("relatorios.datetime")
    def test_intervalo_correto(self, mock_dt, mock_ver, mock_print):
        fake_agora = datetime(2024, 1, 15, 10, 30)
        mock_dt.now.return_value = fake_agora
        mock_ver.return_value = []
        mostrar_extrato_rapido(1, 7)
        inicio_esperado = (fake_agora - timedelta(days=7)).isoformat()
        mock_ver.assert_called_once_with(
            1,
            inicio_esperado,
            fake_agora.isoformat()
        )


# ─── 10. exportar_extrato ─────────────────────────
class TestExportarExtrato(unittest.TestCase):

    @patch("builtins.print")
    @patch("relatorios.ver_extrato")
    def test_sem_transacoes(self, mock_ver, mock_print):
        mock_ver.return_value = []
        exportar_extrato(1)
        mock_print.assert_called_with("Nenhuma transação para exportar.")

    @patch("builtins.print")
    @patch("relatorios.datetime")
    @patch("relatorios.buscar_nome_por_conta")
    @patch("relatorios.ver_extrato")
    def test_cria_arquivo_txt(self, mock_ver, mock_nome, mock_dt, mock_print):
        t = make_transacao(TIPO_DEPOSITO, valor=100.0, saldo_apos=600.0)
        mock_ver.return_value = [t]
        mock_nome.return_value = "Ana Lima"
        mock_dt.now.return_value.strftime.return_value = "2024-01-15"
        mock_dt.fromisoformat.side_effect = datetime.fromisoformat

        nome_arquivo = "extrato_conta_ana_lima_2024-01-15.txt"
        pasta_original = os.getcwd()
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            try:
                exportar_extrato(1)
                with open(nome_arquivo, encoding="utf-8") as f:
                    conteudo = f.read()
            finally:
                os.chdir(pasta_original)

        self.assertIn("EXTRATO BANCÁRIO", conteudo)
        self.assertIn("Depósito", conteudo)
        mock_print.assert_called_with(f"Extrato exportado: {nome_arquivo}")


# ─── 11. exportar_extrato_periodo ─────────────────
class TestExportarExtratoPeriodo(unittest.TestCase):

    @patch("builtins.print")
    @patch("relatorios.ver_extrato_periodo")
    @patch("builtins.input")
    def test_sem_transacoes(self, mock_input, mock_ver, mock_print):
        mock_input.side_effect = ["15/01/2024", "31/01/2024"]
        mock_ver.return_value = []
        exportar_extrato_periodo(1)
        mock_print.assert_called_with("Nenhuma transação no período.")

    @patch("builtins.print")
    @patch("relatorios.buscar_nome_por_conta")
    @patch("relatorios.ver_extrato_periodo")
    @patch("builtins.input")
    def test_cria_arquivo_com_periodo(self, mock_input, mock_ver, mock_nome, mock_print):
        mock_input.side_effect = ["15/01/2024", "31/01/2024"]
        t = make_transacao(TIPO_DEPOSITO, valor=100.0, saldo_apos=600.0)
        mock_ver.return_value = [t]
        mock_nome.return_value = "Ana Lima"

        nome_arquivo = "extrato_ana_lima_15-01-2024_31-01-2024.txt"
        pasta_original = os.getcwd()
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            try:
                exportar_extrato_periodo(1)
                with open(nome_arquivo, encoding="utf-8") as f:
                    conteudo = f.read()
            finally:
                os.chdir(pasta_original)

        self.assertIn("EXTRATO POR PERÍODO", conteudo)
        self.assertIn("15/01/2024 até 31/01/2024", conteudo)
        self.assertIn("Depósito", conteudo)


if __name__ == "__main__":
    unittest.main()
