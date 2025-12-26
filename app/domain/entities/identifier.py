from datetime import datetime
from app.domain.value_objects.identifier_type import IdentifierType
from app.domain.exceptions.domain_exceptions import DomainValidationError


class Identifier:
    """
    Value Object que representa um identificador observável de uma pessoa
    (email, telefone, username, etc.).

    Não representa identidade confirmada, apenas um dado coletado.
    """

    def __init__(
        self,
        tipo: IdentifierType,
        valor: str,
        data_registro: datetime | None = None,
    ):
        self.tipo = tipo
        self.valor = self._normalizar(valor)
        self.data_registro = data_registro or datetime.utcnow()

        self._validar()

    # =========================
    # NORMALIZAÇÃO
    # =========================

    def _normalizar(self, valor: str) -> str:
        if not isinstance(valor, str):
            raise DomainValidationError(
                "Valor do identificador deve ser texto."
            )

        valor = valor.strip()

        if self.tipo in (
            IdentifierType.EMAIL,
            IdentifierType.USERNAME,
        ):
            valor = valor.lower()

        if self.tipo == IdentifierType.TELEFONE:
            valor = "".join(char for char in valor if char.isdigit())

        return valor

    # =========================
    # VALIDAÇÃO
    # =========================

    def _validar(self) -> None:
        if not isinstance(self.tipo, IdentifierType):
            raise DomainValidationError("Tipo de identificador inválido.")

        if not self.valor:
            raise DomainValidationError(
                "Valor do identificador não pode ser vazio."
            )

        # Validações mínimas por tipo
        if self.tipo == IdentifierType.EMAIL and "@" not in self.valor:
            raise DomainValidationError("Email inválido.")

        if self.tipo == IdentifierType.TELEFONE and len(self.valor) < 8:
            raise DomainValidationError("Telefone inválido.")

    # =========================
    # VALUE OBJECT BEHAVIOR
    # =========================

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Identifier):
            return False

        return self.tipo == other.tipo and self.valor == other.valor

    def __hash__(self) -> int:
        return hash((self.tipo, self.valor))