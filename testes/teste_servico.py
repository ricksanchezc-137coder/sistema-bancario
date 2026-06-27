# test_banco_funcoes.py
import unittest
import os
import tempfile
import sqlite3
from unittest.mock import patch

import banco
import servico_v2  # ← ajuste pro nome real do seu arquivo


class TestFuncoesComBanco(unittest.TestCase):

    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        os.close(self.db_fd)
    
        self.patcher = patch('banco.DB_NAME', self.db_path)
        self.patcher.start()
    
        banco.criar_tabelas()
    
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT INTO usuarios (nome, senha) VALUES (?, ?)",
            ("joao", "hash_fake")
        )
        conn.execute(
            "INSERT INTO usuarios (nome, senha) VALUES (?, ?)",
            ("maria", "hash_fake")
        )
        conn.execute(
            "INSERT INTO contas (usuario_id, saldo) VALUES (?, ?)",
            (1, 0.0)
        )
        conn.execute(
            "INSERT INTO contas (usuario_id, saldo) VALUES (?, ?)",
            (2, 0.0)
        )
        conn.commit()   # ← explícito
        conn.close()    # ← fecha antes de depositar abrir a dela
    
        servico_v2.depositar(1, 1000.0)
        servico_v2.depositar(2, 500.0)



    def tearDown(self):
        self.patcher.stop()
        os.unlink(self.db_path)

    # ── depositar ───────────────────────────────────────────

    def test_depositar_aumenta_saldo(self):
        servico_v2.depositar(1, 200.0)

        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT saldo FROM contas WHERE id = 1"
            ).fetchone()

        self.assertEqual(row[0], 1200.0)

    def test_depositar_valor_negativo_deve_falhar(self):
        with self.assertRaises(ValueError):
            servico_v2.depositar(1, -50.0)

    # ── sacar ───────────────────────────────────────────────

    def test_sacar_diminui_saldo(self):
        servico_v2.sacar(1, 300.0)

        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT saldo FROM contas WHERE id = 1"
            ).fetchone()

        self.assertEqual(row[0], 700.0)

    def test_sacar_saldo_insuficiente_deve_falhar(self):
        with self.assertRaises(ValueError):
            servico_v2.sacar(1, 9999.0)

    # ── transferir ──────────────────────────────────────────

    def test_transferir_move_saldo_corretamente(self):
        servico_v2.transferir(1, "maria", 200.0)  # ← "maria", não 2
    
        with sqlite3.connect(self.db_path) as conn:
            origem = conn.execute(
                "SELECT saldo FROM contas WHERE id = 1"
            ).fetchone()
            destino = conn.execute(
                "SELECT saldo FROM contas WHERE id = 2"
            ).fetchone()
    
        self.assertEqual(origem[0], 800.0)
        self.assertEqual(destino[0], 700.0)

    def test_transferir_saldo_insuficiente_deve_falhar(self):
        with self.assertRaises(ValueError):
            servico_v2.transferir(1, "maria", 9999.0)  # ← "maria", não 2
    


if __name__ == '__main__':
    unittest.main()
