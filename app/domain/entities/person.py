from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, List

from app.domain.entities.identifier import Identifier
from app.domain.exceptions.domain_exceptions import DomainValidationError


class Person:
    def __init__(
        self,
        investigation_id: UUID,
        display_name: Optional[str] = None,
    ):
        self.id: UUID = uuid4()
        self.investigation_id: UUID = investigation_id
        self.display_name: Optional[str] = display_name
        self.identifiers: List[Identifier] = []
        self.created_at: datetime = datetime.utcnow()
        self.updated_at: datetime = self.created_at

        self._validate()

    # =========================
    # Regras de Domínio
    # =========================

    def _validate(self) -> None:
        if not self.investigation_id:
            raise DomainValidationError(
                "Person deve estar vinculada a uma investigação."
            )

    # =========================
    # Comportamentos
    # =========================

    def add_identifier(self, identifier: Identifier) -> None:
        if identifier in self.identifiers:
            raise DomainValidationError("Identificador já associado a esta pessoa.")

        self.identifiers.append(identifier)
        self._touch()

    def update_display_name(self, display_name: str) -> None:
        if not display_name or not display_name.strip():
            raise DomainValidationError("Display name inválido.")

        self.display_name = display_name.strip()
        self._touch()

    def _touch(self) -> None:
        self.updated_at = datetime.utcnow()