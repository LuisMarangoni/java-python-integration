import csv
from collections.abc import Iterator
from pathlib import Path


COLUNAS_OBRIGATORIAS = {
    "titulo",
    "descricao",
    "prioridade",
}


def ler_linhas_csv(
        caminho: Path,
) -> Iterator[tuple[int, dict[str, str]]]:
    with caminho.open(
            mode="r",
            encoding="utf-8-sig",
            newline="",
    ) as arquivo:
        leitor = csv.DictReader(arquivo)

        colunas_encontradas = set(leitor.fieldnames or [])
        colunas_ausentes = (
                COLUNAS_OBRIGATORIAS - colunas_encontradas
        )

        if colunas_ausentes:
            nomes = ", ".join(sorted(colunas_ausentes))
            raise ValueError(
                f"Colunas obrigatórias ausentes: {nomes}"
            )

        for numero_linha, dados in enumerate(leitor, start=2):
            yield numero_linha, dados