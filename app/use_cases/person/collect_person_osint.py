from dataclasses import dataclass
from uuid import UUID
from typing import List

from app.domain.entities.evidence import Evidence
from app.domain.exceptions.domain_exceptions import DomainValidationError
from app.domain.value_objects.evidence_type import EvidenceType

from app.interfaces.repositories.investigation_repository import InvestigationRepository
from app.interfaces.repositories.person_repository import PersonRepository
from app.interfaces.repositories.evidence_repository import EvidenceRepository
from app.interfaces.services.osint_service import OSINTService


@dataclass
class CollectPersonOSINTInput:
    investigation_id: UUID
    person_id: UUID
    requested_sources: List[str]


class CollectPersonOSINT:
    """
    Use Case responsável por coletar dados OSINT automatizados
    para uma pessoa investigada, respeitando o planejamento.
    """

    def __init__(
        self,
        investigation_repository: InvestigationRepository,
        person_repository: PersonRepository,
        evidence_repository: EvidenceRepository,
        osint_service: OSINTService,
        coletado_por: str = "OSINT_AUTOMATED",
    ):
        self.investigation_repository = investigation_repository
        self.person_repository = person_repository
        self.evidence_repository = evidence_repository
        self.osint_service = osint_service
        self.coletado_por = coletado_por

    def execute(self, input_data: CollectPersonOSINTInput) -> List[Evidence]:
        # 1. Recuperar investigação
        investigation = self.investigation_repository.get_by_id(
            input_data.investigation_id
        )

        if not investigation:
            raise DomainValidationError("Investigação não encontrada.")

        # 2. Verificar estado da investigação
        if not investigation.esta_ativa():
            raise DomainValidationError(
                "Não é possível coletar OSINT em investigação encerrada."
            )

        if not investigation.planejamento_definido():
            raise DomainValidationError(
                "Investigação não possui planejamento definido."
            )

        # 3. Validar fontes solicitadas
        fontes_nao_autorizadas = set(input_data.requested_sources) - set(
            investigation.allowed_sources
        )

        if fontes_nao_autorizadas:
            raise DomainValidationError(
                f"Fontes não autorizadas pelo planejamento: {fontes_nao_autorizadas}"
            )

        # 4. Recuperar pessoa investigada
        person = self.person_repository.get_by_id(input_data.person_id)

        if not person:
            raise DomainValidationError("Pessoa investigada não encontrada.")

        if person.investigation_id != investigation.id:
            raise DomainValidationError(
                "Pessoa não pertence à investigação informada."
            )

        evidencias_coletadas: List[Evidence] = []

        # 5. Executar OSINT por identificador
        for identifier in person.identifiers:
            resultados = self.osint_service.collect(
                identifier=identifier,
                sources=input_data.requested_sources,
            )

            for resultado in resultados:
                evidence = Evidence(
                    investigation_id=investigation.id,
                    person_id=person.id,
                    tipo=EvidenceType.OSINT_AUTOMATED,
                    fonte=resultado.source,
                    dado=resultado.data,
                    coletado_por=self.coletado_por,
                )

                self.evidence_repository.save(evidence)
                evidencias_coletadas.append(evidence)

        return evidencias_coletadas
