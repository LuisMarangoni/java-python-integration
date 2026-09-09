from typing import Any

import requests

from src.modelos import ChamadoEntrada


class ErroIntegracao(Exception):
    """Erro ocorrido durante a comunicação com a API Java."""


class ClienteChamadosApi:

    def __init__(
            self,
            base_url: str = "http://localhost:8080",
            timeout: float = 5.0,
            sessao: requests.Session | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.sessao = sessao or requests.Session()

    def criar_chamado(
            self,
            chamado: ChamadoEntrada,
    ) -> dict[str, Any]:
        url = f"{self.base_url}/chamados"

        try:
            resposta = self.sessao.post(
                url,
                json=chamado.to_json(),
                timeout=self.timeout,
            )
        except requests.RequestException as erro:
            raise ErroIntegracao(
                "Não foi possível conectar à API de chamados"
            ) from erro

        if resposta.status_code != 201:
            detalhe = self._extrair_detalhe_erro(resposta)

            raise ErroIntegracao(
                f"API retornou HTTP {resposta.status_code}: {detalhe}"
            )

        try:
            return resposta.json()
        except ValueError as erro:
            raise ErroIntegracao(
                "API retornou uma resposta que não é um JSON válido"
            ) from erro

    @staticmethod
    def _extrair_detalhe_erro(
            resposta: requests.Response,
    ) -> str:
        try:
            conteudo = resposta.json()
        except ValueError:
            return resposta.text or "sem detalhes"

        if isinstance(conteudo, dict):
            return str(
                conteudo.get("detail")
                or conteudo.get("error")
                or conteudo
            )

        return str(conteudo)