from dataclasses import dataclass
from uuid import UUID
from typing import Dict, Any, List

from app.domain.exceptions.domain_exceptions import DomainValidationError
from app.interfaces.repositories.investigation_repository import InvestigationRepository
from app.interfaces.repositories.person_repository import PersonRepository
from app.interfaces.repositories.evidence_repository import EvidenceRepository


@dataclass
class GenerateReportInput:
    investigation_id: UUID


class GenerateReport:
    """
    Use Case responsável por gerar um relatório técnico de investigação OSINT.
    O relatório é um artefato imutável e não altera o estado do domínio.
    """

    def __init__(
        self,
        investigation_repository: InvestigationRepository,
        person_repository: PersonRepository,
        evidence_repository: EvidenceRepository,
    ):
        self.investigation_repository = investigation_repository
        self.person_repository = person_repository
        self.evidence_repository = evidence_repository

    def execute(self, input_data: GenerateReportInput) -> Dict[str, Any]:
        # 1. Recuperar investigação
        investigation = self.investigation_repository.get_by_id(
            input_data.investigation_id
        )

        if not investigation:
            raise DomainValidationError("Investigação não encontrada.")

        # 2. Garantir que está encerrada
        if investigation.esta_ativa():
            raise DomainValidationError(
                "Relatório final só pode ser gerado após o encerramento da investigação."
            )

        if not investigation.planejamento_definido():
            raise DomainValidationError(
                "Investigação não possui planejamento definido."
            )

        # 3. Recuperar dados relacionados
        persons = self.person_repository.list_by_investigation(
            investigation.id
        )

        evidences = self.evidence_repository.list_by_investigation(
            investigation.id
        )

        # 4. Organizar evidências por pessoa
        evidencias_por_pessoa: Dict[UUID, List[dict]] = {}
        evidencias_gerais: List[dict] = []

        for evidence in evidences:
            evidence_dict = {
                "id": str(evidence.id),
                "tipo": evidence.tipo.value,
                "fonte": evidence.fonte,
                "dado": evidence.dado,
                "coletado_por": evidence.coletado_por,
                "data_coleta": evidence.data_coleta.isoformat(),
                "hash_integridade": evidence.hash_integridade,
            }

            if evidence.person_id:
                evidencias_por_pessoa.setdefault(
                    evidence.per
