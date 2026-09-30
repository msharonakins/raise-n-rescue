class ApplicationError(Exception):
    """Base exception for application workflow errors."""


class AdopterProfileNotFoundError(ApplicationError):
    """Raised when the authenticated adopter has no profile."""


class AnimalNotFoundError(ApplicationError):
    """Raised when the requested animal does not exist."""


class ApplicationNotFoundError(ApplicationError):
    """Raised when the requested application does not exist."""


class AnimalNotAvailableError(ApplicationError):
    """Raised when the requested animal cannot currently receive applications."""


class ActiveApplicationExistsError(ApplicationError):
    """Raised when the adopter already has an active application for the animal."""


class InvalidApplicationSubmissionError(ApplicationError):
    """Raised when application submission data is invalid."""


class InvalidApplicationStatusTransitionError(ApplicationError):
    """Raised when an application status transition is not allowed."""
