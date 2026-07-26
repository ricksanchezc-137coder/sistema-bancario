import pytest
from servico import transferir
def test_transferir__com_origem_inexistente(banco_temp):
    with pytest.raises(ValueError, match="origem"):
        transferir(origem_id=999, destino_nome="qualquer", valor=10)
