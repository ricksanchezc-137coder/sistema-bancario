import unittest
import sqlite3
import tempfile
import os
import bcrypt
from unittest import mock

import security
from security import registrar_usuario, login


def criar_tabelas(path):
    conn = sqlite3.connect(path)
    conn.execute("""
        CREATE TABLE usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE contas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            saldo REAL NOT NULL DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


class TestRegistrarUsuario(unittest.TestCase):

    def setUp(self):
        self.db_temp = tempfile.NamedTemporaryFile(
            suffix=".db", delete=False
        )
        self.db_path = self.db_temp.name
        self.db_temp.close()
        criar_tabelas(self.db_path)
        self.patcher = mock.patch("banco.DB_NAME", self.db_path)
        self.patcher.start()
        security.tentativas_login.clear()

    def tearDown(self):
        self.patcher.stop()
        os.unlink(self.db_path)

    def test_senha_e_hasheada(self):
        registrar_usuario("joao", "senha123")
        conn = sqlite3.connect(self.db_path)
        row = conn.execute(
            "SELECT senha FROM usuarios WHERE nome = ?",
            ("joao",)
        ).fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertTrue(
            bcrypt.checkpw(
                "senha123".encode("utf-8"),
                row[0].encode("utf-8")
            )
        )

    def test_usuario_duplicado_levanta_erro(self):
        registrar_usuario("joao", "senha123")
        with self.assertRaises(ValueError):
            registrar_usuario("joao", "outrasenha")

    def test_conta_criada_com_saldo_zero(self):
        registrar_usuario("joao", "senha123")
        conn = sqlite3.connect(self.db_path)
        row = conn.execute("""
            SELECT c.saldo FROM contas c
            JOIN usuarios u ON c.usuario_id = u.id
            WHERE u.nome = ?
        """, ("joao",)).fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], 0)


class TestLogin(unittest.TestCase):

    def setUp(self):
        self.db_temp = tempfile.NamedTemporaryFile(
            suffix=".db", delete=False
        )
        self.db_path = self.db_temp.name
        self.db_temp.close()
        criar_tabelas(self.db_path)
        self.patcher = mock.patch("banco.DB_NAME", self.db_path)
        self.patcher.start()
        security.tentativas_login.clear()
        registrar_usuario("joao", "senha123")

    def tearDown(self):
        self.patcher.stop()
        os.unlink(self.db_path)

    def test_login_correto_retorna_usuario(self):
        usuario = login("joao", "senha123")
        self.assertEqual(usuario.nome, "joao")

    def test_senha_errada_levanta_erro(self):
        with self.assertRaises(ValueError):
            login("joao", "errada")

    def test_usuario_inexistente_levanta_erro(self):
        with self.assertRaises(ValueError):
            login("naoexiste", "qualquer")

    def test_bloqueio_por_excesso_de_tentativas(self):
        for _ in range(security.MAX_TENTATIVAS_LOGIN):
            try:
                login("joao", "errada")
            except ValueError:
                pass
        with self.assertRaises(Exception):
            login("joao", "senha123")


if __name__ == "__main__":
    unittest.main()
