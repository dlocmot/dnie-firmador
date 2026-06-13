class DNIeError(Exception):
    """Base exception for DNIe card errors."""


class CardNotFoundError(DNIeError):
    """No smart card reader or card detected."""


class CardNotRecognizedError(DNIeError):
    """Card inserted but not a recognized Peruvian DNIe."""


class PinError(DNIeError):
    """Incorrect PIN or PIN blocked."""


class CertificateError(DNIeError):
    """Failed to read certificate from card."""
