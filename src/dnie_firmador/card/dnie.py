"""Peruvian DNIe certificate extraction and hash signing via pyscard."""

from __future__ import annotations

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from smartcard.CardConnection import CardConnection

from .exceptions import CertificateError, PinError
from .reader import get_dnie_reader

# APDU commands for Peruvian DNIe v2
# These mirror the protocol used by edeustua/peru-dnie
SELECT_MF = [0x00, 0xA4, 0x00, 0x0C]
SELECT_DF_FIRMA = [0x00, 0xA4, 0x01, 0x0C, 0x02, 0x00, 0x11]
SELECT_EF_CERT = [0x00, 0xA4, 0x02, 0x0C, 0x02, 0x00, 0x01]
VERIFY_PIN = [0x00, 0x20, 0x00, 0x01]
INTERNAL_AUTH = [0x00, 0x88, 0x00, 0x00]
SW_OK = (0x90, 0x00)
SW_WRONG_PIN = 0x63


class DNIeSession:
    """Single-use session for certificate reading and document signing."""

    def __init__(self):
        reader = get_dnie_reader()
        self._conn: CardConnection = reader.createConnection()
        self._conn.connect()

    def close(self):
        try:
            self._conn.disconnect()
        except Exception:
            pass

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def read_certificate(self) -> x509.Certificate:
        """Extract the signing certificate from the DNIe."""
        self._select_signing_ef()
        cert_bytes = self._read_binary()
        try:
            return x509.load_der_x509_certificate(bytes(cert_bytes))
        except Exception as e:
            raise CertificateError(f"Could not parse certificate: {e}") from e

    def verify_pin(self, pin: str) -> None:
        """Verify the user PIN. Raises PinError on failure."""
        pin_bytes = [ord(c) for c in pin]
        apdu = VERIFY_PIN + [len(pin_bytes)] + pin_bytes
        _, sw1, sw2 = self._conn.transmit(apdu)
        if (sw1, sw2) != SW_OK:
            retries = sw2 & 0x0F if sw1 == SW_WRONG_PIN else 0
            raise PinError(
                f"Incorrect PIN. Remaining attempts: {retries}"
                if sw1 == SW_WRONG_PIN
                else "PIN blocked or unknown error."
            )

    def sign_hash(self, digest: bytes) -> bytes:
        """Sign a SHA-256 digest using the DNIe private key.

        PIN must be verified before calling this method.
        """
        apdu = INTERNAL_AUTH + [len(digest)] + list(digest) + [0x00]
        data, sw1, sw2 = self._conn.transmit(apdu)
        if (sw1, sw2) != SW_OK:
            raise PinError(f"Signing failed: SW={sw1:02X}{sw2:02X}")
        return bytes(data)

    def _select_signing_ef(self):
        self._transmit_or_raise(SELECT_MF, "SELECT MF")
        self._transmit_or_raise(SELECT_DF_FIRMA, "SELECT DF_FIRMA")
        self._transmit_or_raise(SELECT_EF_CERT, "SELECT EF_CERT")

    def _read_binary(self) -> list[int]:
        result = []
        offset = 0
        while True:
            apdu = [0x00, 0xB0, (offset >> 8) & 0xFF, offset & 0xFF, 0xFF]
            data, sw1, sw2 = self._conn.transmit(apdu)
            if not data:
                break
            result.extend(data)
            offset += len(data)
            if (sw1, sw2) != SW_OK:
                break
        return result

    def _transmit_or_raise(self, apdu: list[int], name: str):
        _, sw1, sw2 = self._conn.transmit(apdu)
        if (sw1, sw2) != SW_OK:
            raise CertificateError(f"{name} failed: SW={sw1:02X}{sw2:02X}")
