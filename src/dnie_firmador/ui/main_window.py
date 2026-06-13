"""Main application window."""

from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from ..card.dnie import DNIeSession
from ..card.exceptions import DNIeError, PinError
from ..signing.signer import PDFSigner
from .pdf_viewer import PDFViewer
from .pin_dialog import PinDialog
from .sig_config import SigConfigPanel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DNIe Firmador")
        self.resize(1100, 750)

        self._pdf_path: Path | None = None
        self._sig_page: int = 0
        self._sig_rect: tuple[float, float, float, float] | None = None

        self._build_ui()

    def _build_ui(self):
        # Toolbar
        tb = QToolBar()
        self.addToolBar(tb)
        open_btn = QPushButton("Open PDF / Abrir PDF")
        open_btn.clicked.connect(self._open_pdf)
        sign_btn = QPushButton("Sign / Firmar")
        sign_btn.clicked.connect(self._sign)
        tb.addWidget(open_btn)
        tb.addWidget(sign_btn)

        # Central layout
        central = QWidget()
        self.setCentralWidget(central)
        h = QHBoxLayout(central)

        self._viewer = PDFViewer()
        self._viewer.sig_rect_changed.connect(self._on_sig_rect)
        h.addWidget(self._viewer, stretch=3)

        # Right panel
        right = QVBoxLayout()
        self._config_panel = SigConfigPanel()
        right.addWidget(self._config_panel)
        self._hint = QLabel(
            "<small>Draw a rectangle on the PDF page<br>to place your signature.<br>"
            "Dibuja un rectángulo en el PDF<br>para posicionar tu firma.</small>"
        )
        self._hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right.addWidget(self._hint)
        right.addStretch()
        h.addLayout(right, stretch=1)

        self.setStatusBar(QStatusBar())

    def _open_pdf(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open PDF", "", "PDF (*.pdf)")
        if path:
            self._pdf_path = Path(path)
            self._viewer.load(path)
            self.statusBar().showMessage(f"Opened: {path}")

    def _on_sig_rect(self, page: int, rect: QRectF):
        self._sig_page = page
        self._sig_rect = (rect.x(), rect.y(), rect.x() + rect.width(), rect.y() + rect.height())
        self.statusBar().showMessage(
            f"Signature position set on page {page + 1} — click Sign to proceed."
        )

    def _sign(self):
        if not self._pdf_path:
            QMessageBox.warning(self, "No PDF", "Please open a PDF first.")
            return
        if not self._sig_rect:
            QMessageBox.warning(self, "No position", "Draw a rectangle on the PDF to place the signature.")
            return

        pin_dlg = PinDialog(self)
        if pin_dlg.exec() != PinDialog.DialogCode.Accepted:
            return
        pin = pin_dlg.pin()

        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save signed PDF", str(self._pdf_path.with_stem(self._pdf_path.stem + "_signed")), "PDF (*.pdf)"
        )
        if not save_path:
            return

        try:
            with DNIeSession() as session:
                session.verify_pin(pin)
                cert = session.read_certificate()
                subj = cert.subject
                name = subj.get_attributes_for_oid(
                    __import__("cryptography.x509.oid", fromlist=["NameOID"]).NameOID.COMMON_NAME
                )[0].value
                dni = name.split()[-1] if name else "00000000"

                appearance = self._config_panel.build_appearance(name, dni)

                signer = PDFSigner()
                signer.sign(
                    pdf_path=self._pdf_path,
                    output_path=Path(save_path),
                    page=self._sig_page,
                    rect=self._sig_rect,
                    appearance=appearance,
                    certificate=cert,
                    sign_callback=session.sign_hash,
                )

            QMessageBox.information(self, "Done / Listo", f"PDF signed successfully.\nGuardado en: {save_path}")
            self.statusBar().showMessage(f"Signed PDF saved to {save_path}")

        except PinError as e:
            QMessageBox.critical(self, "PIN Error", str(e))
        except DNIeError as e:
            QMessageBox.critical(self, "Card Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Signing failed:\n{e}")


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("DNIe Firmador")
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
