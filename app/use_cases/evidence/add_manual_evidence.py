from dataclasses import dataclass
from uuid import UUID
from typing import Optional

from app.domain.entities.evidence import Evidence
from app.domain.exceptions.domain_exceptions import DomainValidationError
from app.interfaces.repositories.investigation_repository import InvestigationRepository
from app.interfaces.repositories.person_repository import PersonRepository
from app.interfaces.repositories.evidence_repository import EvidenceRepository


@dataclass
class AddManualEvidenceInput:
    investigation_id: UUID
    description: str
    source: str
    person_id: Optional[UUID] = None


class AddManualEvidence:
    """
    Use Case responsável por registrar evidência manual
    durante uma investigação OSINT.
    """

    def __init__(
        self,
        investigation_repository: InvestigationRepository,
        evidence_repository: EvidenceRepository,
        person_repository: Optional[PersonRepository] = None,
    ):
        self.investigation_repository = investigation_repository
        self.evidence_repository = evidence_repository
        self.person_repository = person_repository

    def execute(self, input_data: AddManualEvidenceInput) -> Evidence:
        # 1. Verificar se a investigação existe
        investigation = self.investigation_repository.get_by_id(
            input_data.investigation_id
        )

        if not investigation:
            raise DomainValidationError("Investigação não encontrada.")

        # 2. Verificar se a investigação está ativa
        if not investigation.esta_ativa():
            raise DomainValidationError(
                "Não é possível adicionar evidência a uma investigação encerrada."
            )

        # 3. Se houver person_id, validar se a pessoa existe
        if input_data.person_id:
            if not self.person_repository:
                raise DomainValidationError(
                    "Repositório de pessoa não configurado."
                )

            person = self.person_repository.get_by_id(input_data.person_id)
            if not person:
                raise DomainValidationError("Pessoa investigada não encontrada.")

        # 4. Criar a evidência
        evidence = Evidence(
            investigation_id=input_data.investigation_id,
            person_id=input_data.person_id,
            description=input_data.description,
            source=input_data.source,
        )

        # 5. Persistir
        self.evidence_repository.save(evidence)

        # 6. Retornar evidência criada
        return evidence