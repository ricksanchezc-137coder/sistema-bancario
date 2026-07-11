import sys


def obter_separador_caminho():
    if sys.platform == "win32":  # pragma: no cover
        return "\\"
    else:
        return "/"


def processar_dados_opcionais(dados, validador=None):
    if validador is None:  # pragma: no cover
        return dados
    return validador(dados)


try:
    import ujson as json  # pragma: no cover
except ImportError:
    import json
