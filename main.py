from typing import Optional

from banco import buscar_um, criar_tabelas
from excecoes import ContaBloqueadaError, ErroContaBancaria
from models import Conta, Usuario
from relatorios import (
    exportar_csv,
    exportar_extrato,
    exportar_extrato_periodo,
    exportar_json,
    mostrar_extrato,
    mostrar_extrato_periodo,
    mostrar_extrato_rapido,
)
from security import login, registrar_usuario
from servico import depositar, sacar, transferir


def obter_conta(usuario_id: int) -> Optional[Conta]:
    conta = buscar_um(
        "SELECT * FROM contas WHERE usuario_id = ?",
        (usuario_id,)
    )
    if conta:
        return Conta.from_row(conta)
    return None


def submenu_extratos(conta: Conta) -> None:
    print("1 - Extrato")
    print("2 - Extrato por periodo")
    print("3 - Extrato rapido")
    print("4 - Exportar extrato")
    print("5 - Exportar extrato por periodo")
    print("6 - Exportar arquivo csv")
    print("7 - Exportar arquivo json")
    op = input("Escolha: ")

    match op:
        case "1":
            mostrar_extrato(conta.id)
        case "2":
            mostrar_extrato_periodo(conta.id)
        case "3":
            print("1- Hoje")
            print("2- Ultimos 7 dias")
            print("3- ultimos 30 dias")
            op1 = input("Escolha: ")
            match op1:
                 case "1":
                     mostrar_extrato_rapido(conta.id, 1)
                 case "2":
                     mostrar_extrato_rapido(conta.id, 7)
                 case "3":
                     mostrar_extrato_rapido(conta.id, 30)
                 case _:
                     print("Opcao invalida")
        case "4":
            exportar_extrato(conta.id)
        case "5":
            exportar_extrato_periodo(conta.id)
        case "6":
            exportar_csv(conta.id)
        case "7":
            exportar_json(conta.id)
        case _:
            print("Opcao Invalida")


def menu(conta: Conta) -> None:
    while True:
        print("\n--- MENU ---")
        print("1 - Ver saldo")
        print("2 - Depositar")
        print("3 - Sacar")
        print("4 - Transferir")
        print("5 - Menu de extratos")
        print("0 - Sair")
        opcao = input("Escolha: ")

        try:
            match opcao:
                case "1":
                    conta = obter_conta(conta.usuario_id)
                    print(f"Saldo: {conta.saldo}")
                case "2":
                    valor = float(input("Valor: "))
                    depositar(conta.id, valor)
                    print("Depósito realizado")
                case "3":
                    valor = float(input("Valor: "))
                    sacar(conta.id, valor)
                    print("Saque realizado")
                case "4":
                    destino_nome = input("Usuario destino: ")
                    valor = float(input("Valor: "))
                    transferir(conta.id, destino_nome, valor)
                    print("Transferência realizada")
                case "5":
                    submenu_extratos(conta)
                case "0":
                    print("Saindo...")
                    break
                case _:
                    print("Opção inválida")
        except ErroContaBancaria as e:
            print(f"Erro: {e}")


def tentar_login() -> Optional[Usuario]:
    while True:
        nome = input("Usuário: ")
        senha = input("Senha: ")
        try:
            usuario = login(nome, senha)
            print("Login OK")
            return usuario
        except ContaBloqueadaError as e:
            # bloqueio encerra as tentativas, ao contrário de credenciais inválidas
            print(f"Erro: {e}")
            return None
        except ErroContaBancaria as e:
            print(f"Erro: {e}")


def main() -> None:
    criar_tabelas()
    while True:
        print("\n1 - Login")
        print("2 - Registrar")
        print("0 - Encerrar")
        escolha = input("Escolha: ")

        if escolha == "2":
            nome = input("Novo usuário: ")
            senha = input("Senha: ")
            try:
                registrar_usuario(nome, senha)
                print("Usuário criado com sucesso!")
            except ErroContaBancaria as e:
                print(f"Erro: {e}")
        elif escolha == "1":
            usuario = tentar_login()
            if usuario is None:
                break
            conta = obter_conta(usuario.id)
            if not conta:
                print("Conta não encontrada")
                return
            menu(conta)
        elif escolha == "0":
            return
        else:
            print("Opcao invalida")


if __name__ == "__main__":  # pragma: no cover
    main()
