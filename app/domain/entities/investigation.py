from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum
from typing import List, Optional

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
        finalidade: str,
        base_legal: BaseLegal,
        investigation_id: Optional[UUID] = None,
        data_criacao: Optional[datetime] = None,
    ):
        self.id: UUID = investigation_id or uuid4()

        # Dados iniciais (criação)
        self.titulo: str = titulo.strip()
        self.finalidade: str = finalidade.strip()
        self.base_legal: BaseLegal = base_legal

        # Planejamento (definido depois)
        self.objective: Optional[str] = None
        self.scope: Optional[str] = None
        self.allowed_sources: Optional[List[str]] = None
        self.legal_notes: Optional[str] = None

        # Ciclo de vida
        self.status: InvestigationStatus = InvestigationStatus.ABERTA
        self.data_criacao: datetime = data_criacao or datetime.utcnow()
        self.data_encerramento: Optional[datetime] = None

        self._validar_inicial()

    # =========================
    # VALIDAÇÕES
    # =========================

    def _validar_inicial(self) -> None:
        if not self.titulo:
            raise DomainValidationError("Título da investigação é obrigatório.")

        if not self.finalidade:
            raise DomainValidationError("Finalidade da investigação é obrigatória.")

        if not isinstance(self.base_legal, BaseLegal):
            raise DomainValidationError("Base legal inválida ou ausente.")

    # =========================
    # PLANEJAMENTO
    # =========================

    def planejamento_definido(self) -> bool:
        return self.objective is not None

    def definir_planejamento(
        self,
        objective: str,
        scope: str,
        allowed_sources: List[str],
        legal_notes: Optional[str] = None,
    ) -> None:
        if self.planejamento_definido():
            raise DomainValidationError(
                "Planejamento da investigação já foi definido."
            )

        if not objective.strip():
            raise DomainValidationError("Objetivo do planejamento é obrigatório.")

        if not scope.strip():
            raise DomainValidationError("Escopo da investigação é obrigatório.")

        if not allowed_sources:
            raise DomainValidationError(
                "É necessário definir ao menos uma fonte permitida."
            )

        self.objective = objective.strip()
        self.scope = scope.strip()
        self.allowed_sources = allowed_sources
        self.legal_notes = legal_notes.strip() if legal_notes else None

    # =========================
    # CICLO DE VIDA
    # =========================

    def encerrar(self) -> None:
        if self.status == InvestigationStatus.ENCERRADA:
            raise DomainValidationError("Investigação já está encerrada.")

        self.status = InvestigationStatus.ENCERRADA
        self.data_encerramento = datetime.utcnow()

    def esta_ativa(self) -> bool:
        return self.status == InvestigationStatus.ABERTA