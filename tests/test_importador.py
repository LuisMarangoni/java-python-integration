import logging
import requests


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
            "titulo,descricao,prioridade,solicitante_id\n"
            "Erro de rede,Sem internet,ALTA,42\n"
            ",Linha sem titulo,BAIXA,42\n"
            "Impressora offline,Nao imprime,MEDIA,42\n"
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

def test_deve_continuar_apos_resposta_invalida_da_api(
        tmp_path: Path,
        caplog,
):
    caminho = tmp_path / "chamados.csv"

    caminho.write_text(
        (
            "titulo,descricao,prioridade,solicitante_id\n"
            "Erro de rede,Sem internet,ALTA,42\n"
            "Impressora offline,Nao imprime,MEDIA,42\n"
        ),
        encoding="utf-8",
    )

    resposta_invalida = Mock(spec=requests.Response)
    resposta_invalida.status_code = 201
    resposta_invalida.json.return_value = None

    resposta_valida = Mock(spec=requests.Response)
    resposta_valida.status_code = 201
    resposta_valida.json.return_value = {"id": 2}

    sessao = Mock(spec=requests.Session)
    sessao.post.side_effect = [
        resposta_invalida,
        resposta_valida,
    ]

    cliente = ClienteChamadosApi(sessao=sessao)
    caplog.set_level(logging.WARNING)

    resultado = importar_chamados(caminho, cliente)

    assert resultado.total == 2
    assert resultado.sucessos == 1
    assert resultado.falhas == 1
    assert sessao.post.call_count == 2
    assert "Linha 2 rejeitada" in caplog.text
    assert "formato inválido" in caplog.text