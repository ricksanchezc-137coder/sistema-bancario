"""
Plugin customizado do sistema-bancario.
Hooks de relatório: cabeçalho da sessão + resumo final.
"""

def pytest_report_header(config):
    modo_db = "ATIVADO" if config.getoption("--rundb", default=False) else "desativado"
    return f"sistema-bancario | testes de banco de dados: {modo_db}"


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    total_db = 0
    passou_db = 0

    for status, reports in terminalreporter.stats.items():
        for report in reports:
            if getattr(report, "when", None) == "call" and hasattr(report, "keywords") and "db" in report.keywords:
                total_db += 1
                if status == "passed":
                    passou_db += 1

    terminalreporter.write_sep("=", "resumo sistema-bancario")
    terminalreporter.write_line(f"testes marcados 'db' processados: {total_db}")
    terminalreporter.write_line(f"testes 'db' que passaram: {passou_db}")
