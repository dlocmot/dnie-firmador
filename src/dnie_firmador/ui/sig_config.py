"""Signature appearance configuration panel."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..signing.appearance import DEFAULT_SHIELD, SignatureAppearance

ASSETS_DIR = Path(__file__).parent.parent / "assets"


class SigConfigPanel(QWidget):
    """Panel for configuring the visual signature stamp."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._image_path = DEFAULT_SHIELD
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        group = QGroupBox("Signature Appearance / Apariencia de la firma")
        form = QFormLayout(group)

        self._reason = QLineEdit("Soy el autor del documento")
        self._label = QLineEdit("FIRMA\nDIGITAL")

        self._img_btn = QPushButton("Use national coat of arms / Usar escudo nacional")
        self._img_btn.setCheckable(True)
        self._img_btn.setChecked(True)
        self._img_btn.clicked.connect(self._toggle_image)

        self._custom_btn = QPushButton("Choose custom image… / Elegir imagen…")
        self._custom_btn.clicked.connect(self._pick_image)
        self._custom_btn.setEnabled(False)

        form.addRow("Reason / Motivo:", self._reason)
        form.addRow("Stamp label:", self._label)
        form.addRow("Image:", self._img_btn)
        form.addRow("", self._custom_btn)

        layout.addWidget(group)

    def _toggle_image(self, checked: bool):
        if checked:
            self._image_path = DEFAULT_SHIELD
            self._custom_btn.setEnabled(False)
        else:
            self._custom_btn.setEnabled(True)

    def _pick_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select image", "", "Images (*.png *.jpg *.svg)"
        )
        if path:
            self._image_path = Path(path)

    def build_appearance(self, signer_name: str, dni: str) -> SignatureAppearance:
        return SignatureAppearance(
            signer_name=signer_name,
            dni=dni,
            reason=self._reason.text(),
            label_text=self._label.text(),
            image_path=self._image_path,
        )
