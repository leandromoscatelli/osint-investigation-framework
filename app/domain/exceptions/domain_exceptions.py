class DomainValidationError(Exception):
    """
    Exceção lançada quando uma regra de negócio ou legal do domínio é violada.
    Deve ser usada exclusivamente dentro do domínio.
    """

    def __init__(self, message: str):
        super().__init__(message)