from dataclasses import dataclass
from uuid import UUID

from app.domain.exceptions.domain_exceptions import DomainValidationError
from app.interfaces.repositories.investigation_repository import InvestigationRepository


@dataclass
class CloseInvestigationInput:
    investigation_id: UUID


class CloseInvestigation:
    """
    Use Case responsável por encerrar formalmente uma investigação.
    Após o encerramento, nenhuma coleta ou alteração é permitida.
    """

    def __init__(self, investigation_repository: InvestigationRepository):
        self.investigation_repository = investigation_repository

    def execute(self, input_data: CloseInvestigationInput) -> None:
        # 1. Recuperar investigação
        investigation = self.investigation_repository.get_by_id(
            input_data.investigation_id
        )

        if not investigation:
            raise DomainValidationError("Investigação não encontrada.")

        # 2. Verificar se já está encerrada
        if not investigation.esta_ativa():
            raise DomainValidationError(
                "Investigação já está encerrada."
            )

        # 3. (Opcional) Garantir que houve planejamento
        if not investigation.planejamento_definido():
            raise DomainValidationError(
                "Investigação não pode ser encerrada sem planejamento definido."
            )

        # 4. Encerrar investigação
        investigation.encerrar()

        # 5. Persistir estado final
        self.investigation_repository.save(investigation)
