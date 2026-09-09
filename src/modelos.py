from dataclasses import dataclass


PRIORIDADES_VALIDAS = {
    "BAIXA",
    "MEDIA",
    "ALTA",
    "URGENTE",
}


@dataclass(frozen=True)
class ChamadoEntrada:
    titulo: str
    descricao: str
    prioridade: str

    @classmethod
    def from_dict(cls, dados: dict[str, str]) -> "ChamadoEntrada":
        titulo = (dados.get("titulo") or "").strip()
        descricao = (dados.get("descricao") or "").strip()
        prioridade = (dados.get("prioridade") or "").strip().upper()

        erros = []

        if not titulo:
            erros.append("título é obrigatório")

        if not descricao:
            erros.append("descrição é obrigatória")

        if prioridade not in PRIORIDADES_VALIDAS:
            erros.append(
                "prioridade deve ser BAIXA, MEDIA, ALTA ou URGENTE"
            )

        if erros:
            raise ValueError("; ".join(erros))

        return cls(
            titulo=titulo,
            descricao=descricao,
            prioridade=prioridade,
        )

    def to_json(self) -> dict[str, str]:
        return {
            "titulo": self.titulo,
            "descricao": self.descricao,
            "prioridade": self.prioridade,
        }