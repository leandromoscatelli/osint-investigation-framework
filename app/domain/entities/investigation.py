from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum

from app.domain.value_objects.base_legal import BaseLegal
from app.domain.exceptions.domain_exceptions import DomainValidationError


class InvestigationStatus(Enum):
    ABERTA = "ABERTA"
    ENCERRADA = "ENCERRADA"


class Investigation:
    """
    Entidade central do sistema.
    Representa uma investigação OSINT com base legal e ciclo de vida controlado.
    """

    def __init__(
        self,
        titulo: str,
        objetivo: str,
        base_legal: BaseLegal,
        investigation_id: UUID | None = None,
        data_criacao: datetime | None = None,
    ):
        self.id: UUID = investigation_id or uuid4()
        self.titulo: str = titulo.strip()
        self.objetivo: str = objetivo.strip()
        self.base_legal: BaseLegal = base_legal

        self.status: InvestigationStatus = InvestigationStatus.ABERTA
        self.data_criacao: datetime = data_criacao or datetime.utcnow()
        self.data_encerramento: datetime | None = None

        self._validar()

    # =========================
    # REGRAS DE NEGÓCIO
    # =========================

    def _validar(self) -> None:
        if not self.titulo:
            raise DomainValidationError("Título da investigação é obrigatório.")

        if not self.objetivo:
            raise DomainValidationError("Objetivo da investigação é obrigatório.")

        self.validar_base_legal()

    def validar_base_legal(self) -> None:
        if not isinstance(self.base_legal, BaseLegal):
            raise DomainValidationError("Base legal inválida ou ausente.")

    def encerrar(self) -> None:
        if self.status == InvestigationStatus.ENCERRADA:
            raise DomainValidationError("Investigação já está encerrada.")

        self.status = InvestigationStatus.ENCERRADA
        self.data_encerramento = datetime.utcnow()

    def esta_ativa(self) -> bool:
        return self.status == InvestigationStatus.ABERTA