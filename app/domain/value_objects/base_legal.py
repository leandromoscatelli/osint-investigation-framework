from datetime import datetime
from enum import Enum

from app.domain.exceptions.domain_exceptions import DomainValidationError


class LegalBasisType(Enum):
    CONSENTIMENTO = "CONSENTIMENTO"
    LEGITIMO_INTERESSE = "LEGITIMO_INTERESSE"
    OBRIGACAO_LEGAL = "OBRIGACAO_LEGAL"
    EXERCICIO_REGULAR_DIREITO = "EXERCICIO_REGULAR_DIREITO"
    PROTECAO_CREDITO = "PROTECAO_CREDITO"


class BaseLegal:
    """
    Value Object que representa a base legal de uma investigação,
    conforme LGPD (Lei 13.709/2018).
    """

    def __init__(
        self,
        fundamento: LegalBasisType,
        descricao: str,
        consentimento: bool = False,
        data_registro: datetime | None = None,
    ):
        self.fundamento = fundamento
        self.descricao = descricao.strip()
        self.consentimento = consentimento
        self.data_registro = data_registro or datetime.utcnow()

        self._validar()

    # =========================
    # REGRAS DE NEGÓCIO
    # =========================

    def _validar(self) -> None:
        if not isinstance(self.fundamento, LegalBasisType):
            raise DomainValidationError("Fundamento legal inválido.")

        if not self.descricao:
            raise DomainValidationError("Descrição da base legal é obrigatória.")

        if self.fundamento == LegalBasisType.CONSENTIMENTO and not self.consentimento:
            raise DomainValidationError(
                "Base legal CONSENTIMENTO exige consentimento explícito."
            )

    def is_valida(self) -> bool:
        return True

    # =========================
    # VALUE OBJECT BEHAVIOR
    # =========================

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BaseLegal):
            return False

        return (
            self.fundamento == other.fundamento
            and self.descricao == other.descricao
            and self.consentimento == other.consentimento
        )