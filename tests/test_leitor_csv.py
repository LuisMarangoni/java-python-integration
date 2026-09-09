from pathlib import Path

import pytest

from src.leitor_csv import ler_linhas_csv


def test_deve_ler_todas_as_linhas_do_csv():
    caminho = Path("data/chamados.csv")

    linhas = list(ler_linhas_csv(caminho))

    assert len(linhas) == 4
    assert [numero for numero, _ in linhas] == [2, 3, 4, 5]
    assert linhas[0][1]["titulo"] == "Erro de rede"


def test_deve_rejeitar_csv_sem_colunas_obrigatorias(
        tmp_path: Path,
):
    caminho = tmp_path / "invalido.csv"

    caminho.write_text(
        "titulo,descricao\nErro de rede,Sem internet\n",
        encoding="utf-8",
    )

    with pytest.raises(
            ValueError,
            match="Colunas obrigatórias ausentes: prioridade",
    ):
        list(ler_linhas_csv(caminho))