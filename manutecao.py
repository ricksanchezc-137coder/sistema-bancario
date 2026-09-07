import logging
from logging.handlers import RotatingFileHandler
import subprocess
import re
import os
import sys
import shutil
import tarfile
from pathlib import Path
from datetime import datetime

# --- Configuração de logging ---
logger = logging.getLogger("manutencao")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))

file_handler = RotatingFileHandler(
    "manutencao.log",
    maxBytes=1_000_000,
    backupCount=5
)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(
    "%(asctime)s - %(levelname)s - %(funcName)s - %(message)s"
))

logger.addHandler(console_handler)
logger.addHandler(file_handler)

LOCK_FILE = Path("manutencao.lock")


def verificar_trava():
    if LOCK_FILE.exists():
        pid_antigo = LOCK_FILE.read_text().strip()
        try:
            os.kill(int(pid_antigo), 0)
            logger.error(f"Já existe uma execução em andamento (PID {pid_antigo}). Abortando.")
            sys.exit(1)
        except (ProcessLookupError, ValueError):
            logger.warning("Lock antigo encontrado, mas processo não existe mais. Removendo.")
            LOCK_FILE.unlink()
    LOCK_FILE.write_text(str(os.getpid()))


def liberar_trava():
    if LOCK_FILE.exists():
        LOCK_FILE.unlink()


def rodar_testes():
    logger.info("Rodando suíte de testes...")
    resultado = subprocess.run(["pytest"], capture_output=True, text=True)
    saida = resultado.stdout + resultado.stderr

    linhas = saida.splitlines()
    match = re.search(r"=+ (.+) =+", linhas[-1]) if linhas else None
    if match:
        logger.info(f"Resumo dos testes: {match.group(1)}")
    else:
        logger.warning("Não foi possível extrair o resumo do pytest.")

    if resultado.returncode != 0:
        logger.error(f"Testes falharam (código {resultado.returncode}).")
    else:
        logger.info("Todos os testes passaram.")

    return resultado.returncode


def limpar_cache():
    logger.info("Limpando __pycache__...")
    removidos = 0
    for pasta in Path(".").rglob("__pycache__"):
        shutil.rmtree(pasta)
        removidos += 1
        logger.debug(f"Removido: {pasta}")
    logger.info(f"{removidos} pasta(s) de cache removida(s).")


def fazer_backup(destino="backup"):
    Path(destino).mkdir(exist_ok=True)
    nome = f"sistema-bancario-{datetime.now():%Y%m%d-%H%M%S}.tar.gz"
    caminho = Path(destino) / nome

    exclusoes = {".venv", "__pycache__", ".git", ".pytest_cache", "htmlcov", destino}

    logger.info(f"Criando backup em {caminho}...")
    with tarfile.open(caminho, "w:gz") as tar:
        for item in Path(".").iterdir():
            if item.name in exclusoes:
                logger.debug(f"Excluído do backup: {item.name}")
                continue
            tar.add(item)

    logger.info(f"Backup concluído: {caminho} ({caminho.stat().st_size} bytes)")


def main():
    verificar_trava()
    try:
        rodar_testes()
        limpar_cache()
        fazer_backup()
        logger.info("Manutenção concluída com sucesso.")
    finally:
        liberar_trava()


if __name__ == "__main__":
    main()
