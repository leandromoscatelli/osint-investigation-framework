from dataclasses import dataclass

from app.domain.entities.investigation import Investigation
from app.domain.value_objects.base_legal import BaseLegal, LegalBasisType
from app.interfaces.repositories.investigation_repository import InvestigationRepository


@dataclass
class CreateInvestigationInput:
    titulo: str
    objetivo: str
    fundamento_legal: LegalBasisType
    descricao_base_legal: str
    consentimento: bool = False


class CreateInvestigation:
    """
    Use Case responsável por criar uma nova investigação OSINT.
    """

    def __init__(self, investigation_repository: InvestigationRepository):
        self.investigation_repository = investigation_repository

    def execute(self, input_data: CreateInvestigationInput) -> Investigation:
        # 1. Criar Base Legal
        base_legal = BaseLegal(
            fundamento=input_data.fundamento_legal,
            descricao=input_data.descricao_base_legal,
            consentimento=input_data.consentimento,
        )

        # 2. Criar Investigação
        investigation = Investigation(
            titulo=input_data.titulo,
            objetivo=input_data.objetivo,
            base_legal=base_legal,
        )

        # 3. Persistir
        self.investigation_repository.save(investigation)

        # 4. Retornar
        return investigation