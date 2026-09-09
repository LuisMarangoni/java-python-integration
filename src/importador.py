import logging
import os
from dataclasses import dataclass
from pathlib import Path

from src.cliente_api import ClienteChamadosApi, ErroIntegracao
from src.leitor_csv import ler_linhas_csv
from src.modelos import ChamadoEntrada


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ResultadoImportacao:
    total: int
    sucessos: int
    falhas: int


def importar_chamados(
        caminho_csv: Path,
        cliente: ClienteChamadosApi,
) -> ResultadoImportacao:
    total = 0
    sucessos = 0
    falhas = 0

    for numero_linha, dados in ler_linhas_csv(caminho_csv):
        total += 1

        try:
            chamado = ChamadoEntrada.from_dict(dados)
            resposta = cliente.criar_chamado(chamado)
        except (ValueError, ErroIntegracao) as erro:
            falhas += 1
            logger.warning(
                "Linha %s rejeitada: %s",
                numero_linha,
                erro,
            )
            continue

        sucessos += 1
        logger.info(
            "Linha %s importada com ID %s",
            numero_linha,
            resposta.get("id"),
        )

    return ResultadoImportacao(
        total=total,
        sucessos=sucessos,
        falhas=falhas,
    )


def configurar_logging() -> None:
    pasta_logs = Path("logs")
    pasta_logs.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | %(levelname)s | %(message)s"
        ),
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(
                pasta_logs / "importacao.log",
                encoding="utf-8",
                ),
        ],
    )


def main() -> int:
    configurar_logging()

    base_url = os.getenv(
        "CHAMADOS_API_URL",
        "http://localhost:8080",
    )

    caminho_csv = Path(
        os.getenv(
            "CAMINHO_CSV",
            "data/chamados.csv",
        )
    )

    cliente = ClienteChamadosApi(base_url=base_url)

    try:
        resultado = importar_chamados(
            caminho_csv,
            cliente,
        )
    except (FileNotFoundError, ValueError) as erro:
        logger.error(
            "Não foi possível processar o arquivo: %s",
            erro,
        )
        return 2

    logger.info(
        "Resumo: total=%s, sucessos=%s, falhas=%s",
        resultado.total,
        resultado.sucessos,
        resultado.falhas,
    )

    return 1 if resultado.falhas else 0


if __name__ == "__main__":
    raise SystemExit(main())