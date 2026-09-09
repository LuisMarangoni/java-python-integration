import logging
from pathlib import Path
from unittest.mock import Mock

from src.cliente_api import ClienteChamadosApi
from src.importador import importar_chamados


def test_deve_continuar_apos_linha_invalida(
        tmp_path: Path,
        caplog,
):
    caminho = tmp_path / "chamados.csv"

    caminho.write_text(
        (
            "titulo,descricao,prioridade\n"
            "Erro de rede,Sem internet,ALTA\n"
            ",Linha sem titulo,BAIXA\n"
            "Impressora offline,Nao imprime,MEDIA\n"
        ),
        encoding="utf-8",
    )

    cliente = Mock(spec=ClienteChamadosApi)

    cliente.criar_chamado.side_effect = [
        {"id": 1},
        {"id": 2},
    ]

    caplog.set_level(logging.WARNING)

    resultado = importar_chamados(
        caminho,
        cliente,
    )

    assert resultado.total == 3
    assert resultado.sucessos == 2
    assert resultado.falhas == 1
    assert cliente.criar_chamado.call_count == 2
    assert "Linha 3 rejeitada" in caplog.text