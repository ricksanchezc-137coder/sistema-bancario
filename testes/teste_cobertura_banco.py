import banco
import servico_v2
from dados import TIPO_DEPOSITO


def test_buscar_todos_retorna_transacoes_reais(banco_temp, usuario_registrado):
    conta = banco.buscar_um(
        "SELECT contas.id FROM contas JOIN usuarios ON contas.usuario_id = usuarios.id WHERE usuarios.nome = ?",
        (usuario_registrado,)
    )
    conta_id = conta["id"]

    servico_v2.depositar(conta_id=conta_id, valor=150.0)
    servico_v2.depositar(conta_id=conta_id, valor=50.0)

    transacoes = banco.buscar_todos(
        "SELECT * FROM transacoes WHERE conta_destino_id = ?",
        (conta_id,)
    )

    assert len(transacoes) == 2
    valores = sorted(t["valor"] for t in transacoes)
    assert valores == [50.0, 150.0]
    assert all(t["tipo"] == TIPO_DEPOSITO for t in transacoes)
