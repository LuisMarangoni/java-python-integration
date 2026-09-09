import pytest

from src.modelos import ChamadoEntrada


def test_deve_normalizar_chamado_valido():
    dados = {
        "titulo": "  Erro de rede  ",
        "descricao": "  Sem acesso à internet  ",
        "prioridade": "alta",
    }

    chamado = ChamadoEntrada.from_dict(dados)

    assert chamado.titulo == "Erro de rede"
    assert chamado.descricao == "Sem acesso à internet"
    assert chamado.prioridade == "ALTA"


def test_deve_rejeitar_titulo_ausente():
    dados = {
        "titulo": "",
        "descricao": "Sem acesso à internet",
        "prioridade": "ALTA",
    }

    with pytest.raises(
            ValueError,
            match="título é obrigatório",
    ):
        ChamadoEntrada.from_dict(dados)


def test_deve_rejeitar_prioridade_invalida():
    dados = {
        "titulo": "Servidor lento",
        "descricao": "Sistema apresenta lentidão",
        "prioridade": "MUITO_ALTA",
    }

    with pytest.raises(
            ValueError,
            match="prioridade deve ser",
    ):
        ChamadoEntrada.from_dict(dados)