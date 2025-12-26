from dataclasses import dataclass
from uuid import UUID

from app.domain.entities.identifier import Identifier
from app.domain.value_objects.identifier_type import IdentifierType
from app.domain.exceptions.domain_exceptions import DomainValidationError
from app.interfaces.repositories.person_repository import PersonRepository
from app.interfaces.repositories.identifier_repository import IdentifierRepository


@dataclass
class AddIdentifierInput:
    person_id: UUID
    identifier_type: IdentifierType
    value: str
    source: str


class AddIdentifierToPerson:
    """
    Use Case responsável por adicionar um identificador
    a um Subject of Interest (Person).
    """

    def __init__(
        self,
        person_repository: PersonRepository,
        identifier_repository: IdentifierRepository,
    ):
        self.person_repository = person_repository
        self.identifier_repository = identifier_repository

    def execute(self, input_data: AddIdentifierInput) -> Identifier:
        # 1. Verificar se a pessoa existe
        person = self.person_repository.get_by_id(input_data.person_id)

        if not person:
            raise DomainValidationError("Pessoa investigada não encontrada.")

        # 2. Criar o identificador (domínio valida formato e consistência)
        identifier = Identifier(
            person_id=person.id,
            identifier_type=input_data.identifier_type,
            value=input_data.value,
            source=input_data.source,
        )

        # 3. Regra de domínio: associar e evitar duplicidade
        person.add_identifier(identifier)

        # 4. Persistir (ordem importa para cadeia de custódia)
        self.identifier_repository.save(identifier)
        self.person_repository.save(person)

        # 5. Retornar identificador criado
        return identifier