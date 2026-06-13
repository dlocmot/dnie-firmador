"""PC/SC reader detection and card presence monitoring."""

from smartcard.System import readers
from smartcard.util import toHexString

from .exceptions import CardNotFoundError, CardNotRecognizedError

# Known ATR prefixes for Peruvian DNIe v2
PERU_DNIE_ATR_PREFIX = "3B DC 18 FF"


def list_readers() -> list[str]:
    """Return names of all connected PC/SC readers."""
    return [str(r) for r in readers()]


def get_dnie_reader():
    """Return the first reader with a Peruvian DNIe inserted.

    Raises CardNotFoundError if no reader/card found.
    Raises CardNotRecognizedError if card ATR doesn't match DNIe Peru.
    """
    available = readers()
    if not available:
        raise CardNotFoundError("No smart card reader detected. Is pcscd running?")

    for reader in available:
        try:
            conn = reader.createConnection()
            conn.connect()
            atr = toHexString(conn.getATR())
            conn.disconnect()
            if atr.upper().startswith(PERU_DNIE_ATR_PREFIX):
                return reader
        except Exception:
            continue

    raise CardNotRecognizedError(
        "No Peruvian DNIe detected. Insert your DNIe and try again."
    )
