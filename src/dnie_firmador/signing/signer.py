"""PDF signing orchestration using pyHanko interrupted signing mode."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign import fields, signers
from pyhanko.sign.fields import SigFieldSpec

from .appearance import SignatureAppearance


class PDFSigner:
    """Orchestrates the two-phase pyHanko interrupted signing flow."""

    def sign(
        self,
        pdf_path: Path,
        output_path: Path,
        page: int,
        rect: tuple[float, float, float, float],
        appearance: SignatureAppearance,
        certificate: x509.Certificate,
        sign_callback,
    ) -> None:
        """Sign a PDF and write the result to output_path.

        Args:
            pdf_path: Path to the input PDF.
            output_path: Path where the signed PDF will be saved.
            page: 0-based page index for the signature field.
            rect: (x0, y0, x1, y1) in PDF points from bottom-left.
            appearance: Visual stamp configuration.
            certificate: Signer's X.509 certificate from the DNIe.
            sign_callback: Callable(digest: bytes) -> bytes that signs the hash
                           using the DNIe private key (card layer).
        """
        timestamp = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M:%S%z")
        stamp_png = appearance.render_png(timestamp)

        with open(pdf_path, "rb") as f:
            writer = IncrementalPdfFileWriter(f)
            fields.append_signature_field(
                writer,
                SigFieldSpec("Signature1", on_page=page, box=rect),
            )

            signer = signers.SimpleSigner(
                signing_cert=certificate,
                signing_key=None,
                cert_registry=signers.SimpleCertificateStore([certificate]),
            )

            # Phase 1: prepare — compute the hash to sign
            prep_digest, tbs_document, sig_obj = signers.sign_pdf_prepare(
                writer,
                signers.PdfSignatureMetadata(field_name="Signature1"),
                signer=signer,
            )

            # Phase 2: sign the hash externally with the DNIe
            signature_bytes = sign_callback(prep_digest.document_digest)

            # Phase 3: embed the signature
            signers.sign_pdf_embed(tbs_document, sig_obj, signature_bytes)

            output_path.write_bytes(tbs_document.getvalue())
