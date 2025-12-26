from dataclasses import dataclass
from uuid import UUID
from typing import List, Optional

from app.domain.exceptions.domain_exceptions import DomainValidationError
from app.interfaces.repositories.investigation_repository import InvestigationRepository


@dataclass
class PlanInvestigationInput:
    investigation_id: UUID
    objective: str
    scope: str
    allowed_sources: List[str]
    legal_notes: Optional[str] = None


class PlanInvestigation:
    """
    Use Case responsável por formalizar o planejamento de uma investigação OSINT.
    """

    def __init__(self, investigation_repository: InvestigationRepository):
        self.investigation_repository = investigation_repository

    def execute(self, input_data: PlanInvestigationInput) -> None:
        # 1. Recuperar investigação
        investigation = self.investigation_repository.get_by_id(
            input_data.investigation_id
        )

        if not investigation:
            raise DomainValidationError("Investigação não encontrada.")

        # 2. Verificar se está ativa
        if not investigation.esta_ativa():
            raise DomainValidationError(
                "Não é possível planejar uma investigação encerrada."
            )

        # 3. Verificar se já existe planejamento
        if investigation.planejamento_definido():
            raise DomainValidationError(
                "Planejamento da investigação já foi definido."
            )

        # 4. Aplicar planejamento
        investigation.definir_planejamento(
            objective=input_data.objective,
            scope=input_data.scope,
            allowed_sources=input_data.allowed_sources,
            legal_notes=input_data.legal_notes,
        )

        # 5. Persistir alterações
        self.investigation_repository.save(investigation)