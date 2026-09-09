from unittest.mock import Mock

import pytest
import requests

from src.cliente_api import ClienteChamadosApi, ErroIntegracao
from src.modelos import ChamadoEntrada


def criar_chamado_exemplo() -> ChamadoEntrada:
    return ChamadoEntrada(
        titulo="Erro de rede",
        descricao="Sem conexão",
        prioridade="ALTA",
    )


def test_deve_enviar_chamado_e_retornar_json():
    sessao = Mock(spec=requests.Session)
    resposta = Mock(spec=requests.Response)

    resposta.status_code = 201
    resposta.json.return_value = {
        "id": 1,
        "titulo": "Erro de rede",
    }

    sessao.post.return_value = resposta

    cliente = ClienteChamadosApi(
        base_url="http://localhost:8080/",
        timeout=3.0,
        sessao=sessao,
    )

    resultado = cliente.criar_chamado(
        criar_chamado_exemplo()
    )

    assert resultado["id"] == 1

    sessao.post.assert_called_once_with(
        "http://localhost:8080/chamados",
        json={
            "titulo": "Erro de rede",
            "descricao": "Sem conexão",
            "prioridade": "ALTA",
        },
        timeout=3.0,
    )


def test_deve_tratar_erro_retornado_pela_api():
    sessao = Mock(spec=requests.Session)
    resposta = Mock(spec=requests.Response)

    resposta.status_code = 400
    resposta.json.return_value = {
        "detail": "Dados inválidos"
    }

    sessao.post.return_value = resposta

    cliente = ClienteChamadosApi(sessao=sessao)

    with pytest.raises(
            ErroIntegracao,
            match="HTTP 400: Dados inválidos",
    ):
        cliente.criar_chamado(criar_chamado_exemplo())


def test_deve_tratar_falha_de_conexao():
    sessao = Mock(spec=requests.Session)

    sessao.post.side_effect = requests.ConnectionError(
        "conexão recusada"
    )

    cliente = ClienteChamadosApi(sessao=sessao)

    with pytest.raises(
            ErroIntegracao,
            match="Não foi possível conectar",
    ):
        cliente.criar_chamado(criar_chamado_exemplo())