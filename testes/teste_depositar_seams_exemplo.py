
import banco
import servico
from datetime import datetime


def _conta_id_de(usuario_registrado):
    conta = banco.buscar_um(
        "SELECT contas.id FROM contas JOIN usuarios ON contas.usuario_id = usuarios.id WHERE usuarios.nome = ?",
        (usuario_registrado,)
    )
    return conta["id"]


def test_depositar_grava_data_hora_exata(banco_temp, usuario_registrado):
    conta_id = _conta_id_de(usuario_registrado)
    data_fixa = datetime(2026, 1, 1, 12, 0, 0)

    servico.depositar(conta_id=conta_id, valor=100.0, agora=data_fixa)

    transacao = banco.buscar_um(
        "SELECT data_hora FROM transacoes WHERE conta_destino_id = ? ORDER BY id DESC LIMIT 1",
        (conta_id,)
    )

    assert transacao["data_hora"] == data_fixa.isoformat()


def test_depositar_usa_now_quando_agora_nao_informado(banco_temp, usuario_registrado):
    conta_id = _conta_id_de(usuario_registrado)

    antes = datetime.now()
    servico.depositar(conta_id=conta_id, valor=50.0)
    depois = datetime.now()

    transacao = banco.buscar_um(
        "SELECT data_hora FROM transacoes WHERE conta_destino_id = ? ORDER BY id DESC LIMIT 1",
        (conta_id,)
    )
    data_hora_salva = datetime.fromisoformat(transacao["data_hora"])

    assert antes <= data_hora_salva <= depois
