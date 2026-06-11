class DomainError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class OrderValidationError(DomainError):
    pass


class ImageValidationError(DomainError):
    pass


class FeedbackValidationError(DomainError):
    pass
