import csv
from datetime import datetime, timedelta
from banco import buscar_todos, buscar_um
from dados import TIPO_DEPOSITO, TIPO_SAQUE, TIPO_TRANSFERENCIA_ENVIADA, TIPO_TRANSFERENCIA_RECEBIDA

def exportar_csv(conta_id):
    transacoes = buscar_todos("""
        SELECT data_hora, tipo, valor, saldo_apos
        FROM transacoes
        WHERE
        (
            tipo = ? AND conta_destino_id = ?)
            OR (tipo = ? AND conta_origem_id = ?)
            OR (tipo = ? AND conta_origem_id = ?)
            OR (tipo = ? AND conta_destino_id = ?)
        ORDER BY data_hora DESC
    """, (
        TIPO_DEPOSITO, conta_id,
        TIPO_SAQUE, conta_id,
        TIPO_TRANSFERENCIA_ENVIADA, conta_id,
        TIPO_TRANSFERENCIA_RECEBIDA, conta_id
    ))

    with open(
        "extrato.csv",
        "w",
        newline="",
        encoding="utf-8"
    ) as arquivo:

        escritor = csv.writer(arquivo)

        escritor.writerow([
            "data",
            "tipo",
            "valor",
            "saldo_apos"
        ])

        for transacao in transacoes:

            data = datetime.fromisoformat(
                transacao["data_hora"]
            )

            data_formatada = data.strftime(
                "%d/%m/%Y %H:%M"
            )

            escritor.writerow([
                data_formatada,
                transacao["tipo"],
                transacao["valor"],
                transacao["saldo_apos"]
            ])

    print("Extrato exportado.")



# ------------------------
# EXTRATO
# ------------------------

def ver_extrato(conta_id: int):
    query = """
    SELECT 
        tipo,
        conta_origem_id,
        conta_destino_id,
        valor,
        saldo_apos,
        data_hora
    FROM transacoes
    WHERE
        (tipo = ?  AND conta_destino_id = ?)
        OR (tipo = ?  AND conta_origem_id = ?)
        OR (tipo = ?  AND conta_origem_id = ?)
        OR (tipo = ?  AND conta_destino_id = ?)
    ORDER BY data_hora DESC
    """
    return buscar_todos(query, (
        TIPO_DEPOSITO,        conta_id,
        TIPO_SAQUE,        conta_id,
        TIPO_TRANSFERENCIA_ENVIADA,  conta_id,
        TIPO_TRANSFERENCIA_RECEBIDA, conta_id
    ))

def formatar_transacao(t, conta_id):
    tipo = t["tipo"]
    valor = t["valor"]
    saldo_apos = t["saldo_apos"]

    data = datetime.fromisoformat(
        t["data_hora"]
    )

    data_formatada = data.strftime(
        "%d/%m/%Y %H:%M"
    )

    if tipo == TIPO_DEPOSITO:

        return (
            f"[{data_formatada}] "
            f"+ R${valor:.2f} "
            f"(Depósito) | "
            f"Saldo: R${saldo_apos:.2f}"
        )

    elif tipo == TIPO_SAQUE:

        return (
            f"[{data_formatada}] "
            f"- R${valor:.2f} "
            f"(Saque) | "
            f"Saldo: R${saldo_apos:.2f}"
        )

    elif tipo == TIPO_TRANSFERENCIA_ENVIADA:

        nome_destino = buscar_nome_por_conta(
            t["conta_destino_id"]
        )

        return (
            f"[{data_formatada}] "
            f"- R${valor:.2f} "
            f"(Enviado para "
            f"{nome_destino}) | "
            f"Saldo: R${saldo_apos:.2f}"
        )

    elif tipo == TIPO_TRANSFERENCIA_RECEBIDA:

        nome_origem = buscar_nome_por_conta(
            t["conta_origem_id"]
        )

        return (
            f"[{data_formatada}] "
            f"+ R${valor:.2f} "
            f"(Recebido de "
            f"{nome_origem}) | "
            f"Saldo: R${saldo_apos:.2f}"
        )

    return "Transação desconhecida"

def mostrar_extrato(conta_id):
    transacoes = ver_extrato(conta_id)

    if not transacoes:
        print("Nenhuma transação encontrada.")
        return

    print("\n=== EXTRATO ===")

    for t in transacoes:
        linha = formatar_transacao(
            t,
            conta_id
        )
        print(linha)

def buscar_nome_por_conta(conta_id):
    query = """
    SELECT u.nome
    FROM contas c
    JOIN usuarios u ON c.usuario_id = u.id
    WHERE c.id = ?
    """
    resultado = buscar_um(query, (conta_id,))
    return resultado["nome"] if resultado else "Desconhecido"



def ver_extrato_periodo(conta_id, data_inicio, data_fim):
    query = """
    SELECT 
        tipo, 
        conta_origem_id, 
        conta_destino_id, 
        valor, 
        saldo_apos, 
        data_hora
    FROM transacoes
    WHERE
        (
            (tipo = ? AND conta_destino_id = ?)
            OR (tipo = ? AND conta_origem_id = ?)
            OR (tipo = ? AND conta_origem_id = ?)
            OR (tipo = ? AND conta_destino_id = ?)
        )
        AND data_hora BETWEEN ? AND ?
    ORDER BY data_hora DESC
    """

    return buscar_todos(query, (
        TIPO_DEPOSITO, conta_id,
        TIPO_SAQUE, conta_id,
        TIPO_TRANSFERENCIA_ENVIADA, conta_id,
        TIPO_TRANSFERENCIA_RECEBIDA, conta_id,
        data_inicio,
        data_fim
    ))


def formatar_data_iso(data_str, fim=False):
    data = datetime.strptime(data_str, "%d/%m/%Y")

    if fim:
        data = data.replace(hour=23, minute=59, second=59)
    else:
        data = data.replace(hour=0, minute=0, second=0)

    return data.isoformat()
    

def mostrar_extrato_periodo(conta_id):
    data_inicio = input("Data início (dd/mm/aaaa): ")
    data_fim = input("Data fim (dd/mm/aaaa): ")

    inicio_iso = formatar_data_iso(data_inicio)
    fim_iso = formatar_data_iso(data_fim, fim=True)

    transacoes = ver_extrato_periodo(conta_id, inicio_iso, fim_iso)

    if not transacoes:
        print("Nenhuma transação no período.")
        return

    print("\n=== EXTRATO POR PERÍODO ===")

    for t in transacoes:
        linha=formatar_transacao(
            t,
            conta_id
        )
        print(linha)

def mostrar_extrato_rapido(conta_id, dias):
    agora = datetime.now()

    inicio = agora - timedelta(days=dias)

    transacoes = ver_extrato_periodo(
        conta_id,
        inicio.isoformat(),
        agora.isoformat()
    )

    if not transacoes:
        print("Nenhuma transação encontrada.")
        return

    print(f"\n=== ÚLTIMOS {dias} DIAS ===")

    for t in transacoes:
        linha=formatar_transacao(
            t,
            conta_id
        )
        print(linha)


def exportar_extrato(conta_id):
    transacoes = ver_extrato(conta_id)

    if not transacoes:
        print("Nenhuma transação para exportar.")
        return
    #busca nome
    nome_usuario= buscar_nome_por_conta(conta_id)
    #remove maisculos e espacos
    nome_usuario= nome_usuario.lower().replace(" ", "_")
    #resgitra data atual
    data_arquivo= datetime.now().strftime("%Y-%m-%d")

    nome_arquivo = (
        f"extrato_conta_{nome_usuario}_{data_arquivo}.txt"
    )

    with open(nome_arquivo, "w", encoding="utf-8") as arquivo:

        arquivo.write("=== EXTRATO BANCÁRIO ===\n\n")

        for t in transacoes:
            linha=formatar_transacao(
            t,
            conta_id
        )

            arquivo.write(linha + "\n")

    print(f"Extrato exportado: {nome_arquivo}")



def exportar_extrato_periodo(conta_id):
    data_inicio = input(
        "Data início (dd/mm/aaaa): "
    )

    data_fim = input(
        "Data fim (dd/mm/aaaa): "
    )

    inicio_iso = formatar_data_iso(data_inicio)

    fim_iso = formatar_data_iso(
        data_fim,
        fim=True
    )

    transacoes = ver_extrato_periodo(
        conta_id,
        inicio_iso,
        fim_iso
    )

    if not transacoes:
        print("Nenhuma transação no período.")
        return

    nome_usuario = buscar_nome_por_conta(
        conta_id
    )

    nome_usuario = (
        nome_usuario
        .lower()
        .replace(" ", "_")
    )

    nome_arquivo = (
        f"extrato_"
        f"{nome_usuario}_"
        f"{data_inicio.replace('/', '-')}_"
        f"{data_fim.replace('/', '-')}.txt"
    )

    with open(
        nome_arquivo,
        "w",
        encoding="utf-8"
    ) as arquivo:

        arquivo.write(
            "=== EXTRATO POR PERÍODO ===\n\n"
        )

        arquivo.write(
            f"Período: "
            f"{data_inicio} até {data_fim}\n\n"
        )

        for t in transacoes:
            linha=formatar_transacao(
                t,
                conta_id
            )

            arquivo.write(linha + "\n")

    print(
        f"Extrato exportado: "
        f"{nome_arquivo}"
    )









