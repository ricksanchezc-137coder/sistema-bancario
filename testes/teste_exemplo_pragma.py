# teste_exemplo_pragma.py
from exemplo_pragma import obter_separador_caminho, processar_dados_opcionais


def teste_processar_dados_sem_validador():
    resultado = processar_dados_opcionais({"a": 1})
    assert resultado == {"a": 1}


def teste_processar_dados_com_validador():
    validador = lambda dados: {**dados, "validado": True}
    resultado = processar_dados_opcionais({"a": 1}, validador)
    assert resultado == {"a": 1, "validado": True}


def teste_separador_retorna_string():
    # não testamos qual valor exato (depende de plataforma),
    # só que a função sempre retorna algo usável
    assert obter_separador_caminho() in ("/", "\\")
