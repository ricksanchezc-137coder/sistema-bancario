from banco import criar_tabelas, buscar_um
from security import registrar_usuario, login
from servico_v2 import depositar, sacar, transferir
from relatorios import exportar_csv, mostrar_extrato, mostrar_extrato_periodo, mostrar_extrato_rapido, exportar_extrato, exportar_extrato_periodo
from models import Conta

def obter_conta(usuario_id):
    conta = buscar_um(
        "SELECT * FROM contas WHERE usuario_id = ?",
        (usuario_id,)
    )
    if conta:
        return Conta.from_row(conta)
    return None


def menu(conta):
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
            if opcao == "1":
                conta = obter_conta(conta.usuario_id)
                print(f"Saldo: {conta.saldo}")

            elif opcao == "2":
                valor = float(input("Valor: "))
                depositar(conta.id, valor)
                print("Depósito realizado")

            elif opcao == "3":
                valor = float(input("Valor: "))
                sacar(conta.id, valor)
                print("Saque realizado")

            elif opcao == "4":
                destino_nome = input("Usuario destino: ")
                valor = float(input("Valor: "))
                transferir(conta.id, destino_nome, valor)
                print("Transferência realizada")

            elif opcao == "5":
                print("1 - Extrato")
                print("2 - Extrato por periodo")
                print("3 - Extrato rapido")
                print("4 - Exportar extrato")
                print("5 - Exportar extrato por periodo")
                print("6 - Exportar arquivo csv")
                op = input("Escolha: ")
                if op == "1":
                    mostrar_extrato(conta.id)
                elif op == "2":
                    mostrar_extrato_periodo(conta.id)
                elif op == "3":
                    print("1- Hoje")
                    print("2- Ultimos 7 dias")
                    print("3- ultimos 30 dias")
                    op1 = input("Escolha: ")
                    if op1 == "1":
                        mostrar_extrato_rapido(conta.id, 1)
                    elif op1 == "2":
                        mostrar_extrato_rapido(conta.id, 7)
                    elif op1 == "3":
                        mostrar_extrato_rapido(conta.id, 30)
                    else:
                        print("Opcao invalida")
                elif op == "4":
                    exportar_extrato(conta.id)
                elif op == "5":
                    exportar_extrato_periodo(conta.id)
                elif op == "6":
                    exportar_csv(conta.id)
                else:
                    print("Opcao Invalida")

            elif opcao == "0":
                print("Saindo...")
                break

            else:
                print("Opção inválida")

        except ValueError as e:
            print(f"Erro: {e}")


def main():
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
            except ValueError as e:
                print(f"Erro: {e}")

        elif escolha == "1":
            while True:
                nome = input("Usuário: ")
                senha = input("Senha: ")
                try:
                    usuario = login(nome, senha)
                    print("Login OK")
                    break
                except ValueError as e:
                    print(f"Erro: {e}")
                except Exception as e:
                    print(f"Erro: {e}")
                    break

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


if __name__ == "__main__":
    main()
