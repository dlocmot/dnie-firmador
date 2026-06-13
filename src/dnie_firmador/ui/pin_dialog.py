"""Secure PIN entry dialog."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QLineEdit, QVBoxLayout


class PinDialog(QDialog):
    """Modal dialog for secure DNIe PIN entry."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("DNIe PIN")
        self.setModal(True)
        self.setFixedWidth(300)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Enter your DNIe PIN:"))

        self._pin_input = QLineEdit()
        self._pin_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._pin_input.setMaxLength(8)
        self._pin_input.returnPressed.connect(self.accept)
        layout.addWidget(self._pin_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def pin(self) -> str:
        return self._pin_input.text()
