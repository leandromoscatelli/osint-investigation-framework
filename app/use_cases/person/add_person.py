from dataclasses import dataclass
from uuid import UUID
from typing import Optional

from app.domain.entities.person import Person
from app.domain.exceptions.domain_exceptions import DomainValidationError
from app.interfaces.repositories.investigation_repository import InvestigationRepository
from app.interfaces.repositories.person_repository import PersonRepository


@dataclass
class AddPersonInput:
    investigation_id: UUID
    display_name: Optional[str] = None


class AddPersonToInvestigation:
    """
    Use Case responsável por adicionar um Subject of Interest (Person)
    a uma investigação ativa.
    """

    def __init__(
        self,
        investigation_repository: InvestigationRepository,
        person_repository: PersonRepository,
    ):
        self.investigation_repository = investigation_repository
        self.person_repository = person_repository

    def execute(self, input_data: AddPersonInput) -> Person:
        # 1. Verificar se a investigação existe
        investigation = self.investigation_repository.get_by_id(
            input_data.investigation_id
        )

        if not investigation:
            raise DomainValidationError("Investigação não encontrada.")

        # 2. Verificar se a investigação está ativa
        if not investigation.esta_ativa():
            raise DomainValidationError(
                "Não é possível adicionar pessoa a uma investigação encerrada."
            )

        # 3. Criar Subject of Interest
        person = Person(
            investigation_id=investigation.id,
            display_name=input_data.display_name,
        )

        # 4. Persistir
        self.person_repository.save(person)

        # 5. Retornar
        return person