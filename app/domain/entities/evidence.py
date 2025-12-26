from datetime import datetime
from uuid import UUID, uuid4
import json
import hashlib
from typing import Optional, Dict, Any

from app.domain.value_objects.evidence_type import EvidenceType
from app.domain.exceptions.domain_exceptions import DomainValidationError


class Evidence:
    """
    Entidade que representa uma evidência coletada durante uma investigação OSINT.
    Evidências são registros factuais e não devem ser alteradas após criação.
    """

    def __init__(
        self,
        investigation_id: UUID,
        tipo: EvidenceType,
        fonte: str,
        dado: Dict[str, Any],
        coletado_por: str,
        person_id: Optional[UUID] = None,
        evidence_id: Optional[UUID] = None,
        data_coleta: Optional[datetime] = None,
    ):
        self.id: UUID = evidence_id or uuid4()
        self.investigation_id: UUID = investigation_id
        self.person_id: Optional[UUID] = person_id

        self.tipo: EvidenceType = tipo
        self.fonte: str = fonte.strip()
        self.dado: Dict[str, Any] = dado

        self.coletado_por: str = coletado_por.strip()
        self.data_coleta: datetime = data_coleta or datetime.utcnow()

        self._validar()

        self.hash_integridade: str = self._gerar_hash()

    # =========================
    # REGRAS INTERNAS
    # =========================

    def _validar(self) -> None:
        if not self.investigation_id:
            raise DomainValidationError(
                "Evidência deve estar vinculada a uma investigação válida."
            )

        if not isinstance(self.tipo, EvidenceType):
            raise DomainValidationError("Tipo de evidência inválido.")

        if not self.fonte:
            raise DomainValidationError("Fonte da evidência é obrigatória.")

        if not isinstance(self.dado, dict) or not self.dado:
            raise DomainValidationError(
                "Dado da evidência deve ser um dicionário não vazio."
            )

        if not self.coletado_por:
            raise DomainValidationError(
                "Responsável pela coleta é obrigatório."
            )

    def _gerar_hash(self) -> str:
        """
        Gera hash de integridade baseado no conteúdo completo da evidência.
        """

        payload = {
            "investigation_id": str(self.investigation_id),
            "person_id": str(self.person_id) if self.person_id else None,
            "tipo": self.tipo.value,
            "fonte": self.fonte,
            "dado": self.dado,
            "coletado_por": self.coletado_por,
            "data_coleta": self.data_coleta.isoformat(),
        }

        conteudo_serializado = json.dumps(
            payload, sort_keys=True, ensure_ascii=False
        ).encode("utf-8")

        return hashlib.sha256(conteudo_serializado).hexdigest()