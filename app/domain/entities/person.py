from datetime import datetime
from uuid import UUID, uuid4
from typing import List

from app.domain.entities.identifier import Identifier
from app.domain.exceptions.domain_exceptions import DomainValidationError


class Person:
    """
    Entidade que representa uma pessoa investigada dentro de uma investigação OSINT.
    """

    def __init__(
        self,
        investigation_id: UUID,
        nome: str,
        person_id: UUID | None = None,
        identificadores: List[Identifier] | None = None,
        data_criacao: datetime | None = None,
    ):
        self.id: UUID = person_id or uuid4()
        self.investigation_id: UUID = investigation_id
        self.nome: str = nome.strip()

        self.identificadores: List[Identifier] = identificadores or []
        self.data_criacao: datetime = data_criacao or datetime.utcnow()

        self._validar()

    # =========================
    # REGRAS DE NEGÓCIO
    # =========================

    def _validar(self) -> None:
        if not self.investigation_id:
            raise DomainValidationError(
                "Pessoa deve estar vinculada a uma investigação válida."
            )

        if not self.nome:
            raise DomainValidationError("Nome da pessoa é obrigatório.")

    def adicionar_identificador(self, identificador: Identifier) -> None:
        if not isinstance(identificador, Identifier):
            raise DomainValidationError("Identificador inválido.")

        if self.possui_identificador(identificador):
            return  # evita duplicação

        self.identificadores.append(identificador)

    def possui_identificador(self, identificador: Identifier) -> bool:
        return identificador in self.identificadores
