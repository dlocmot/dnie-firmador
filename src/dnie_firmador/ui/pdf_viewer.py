"""Interactive PDF viewer with click-to-place signature rectangle."""

from __future__ import annotations

import fitz  # PyMuPDF
from PyQt6.QtCore import QPoint, QRect, QRectF, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QImage, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import QLabel, QScrollArea, QSizePolicy, QVBoxLayout, QWidget

RENDER_DPI = 150


class PDFPageWidget(QLabel):
    """Single PDF page rendered as an image; supports dragging a signature rectangle."""

    sig_rect_changed = pyqtSignal(QRectF)  # rect in PDF points

    def __init__(self, page: fitz.Page, parent=None):
        super().__init__(parent)
        self._page = page
        self._scale = RENDER_DPI / 72.0
        self._drag_start: QPoint | None = None
        self._drag_rect: QRect | None = None
        self._render()
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def _render(self):
        mat = fitz.Matrix(self._scale, self._scale)
        pix = self._page.get_pixmap(matrix=mat, alpha=False)
        img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
        self._pixmap_base = QPixmap.fromImage(img)
        self.setPixmap(self._pixmap_base)
        self.resize(self._pixmap_base.size())

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start = event.pos()
            self._drag_rect = None

    def mouseMoveEvent(self, event):
        if self._drag_start:
            self._drag_rect = QRect(self._drag_start, event.pos()).normalized()
            self._repaint_with_rect()

    def mouseReleaseEvent(self, event):
        if self._drag_start and self._drag_rect:
            self.sig_rect_changed.emit(self._screen_to_pdf(self._drag_rect))
        self._drag_start = None

    def _repaint_with_rect(self):
        pm = self._pixmap_base.copy()
        painter = QPainter(pm)
        pen = QPen(QColor(180, 0, 0), 2, Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.drawRect(self._drag_rect)
        painter.end()
        self.setPixmap(pm)

    def _screen_to_pdf(self, rect: QRect) -> QRectF:
        s = self._scale
        # PDF coordinates: origin at bottom-left
        page_h = self._page.rect.height
        x0 = rect.left() / s
        y0 = page_h - rect.bottom() / s
        x1 = rect.right() / s
        y1 = page_h - rect.top() / s
        return QRectF(x0, y0, x1 - x0, y1 - y0)


class PDFViewer(QScrollArea):
    """Scrollable viewer showing all pages of a PDF."""

    sig_rect_changed = pyqtSignal(int, QRectF)  # (page_index, rect_in_pdf_pts)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._doc: fitz.Document | None = None
        self._page_widgets: list[PDFPageWidget] = []
        container = QWidget()
        self._layout = QVBoxLayout(container)
        self._layout.setSpacing(8)
        self.setWidget(container)
        self.setWidgetResizable(False)

    def load(self, path: str):
        self._doc = fitz.open(path)
        for w in self._page_widgets:
            w.deleteLater()
        self._page_widgets.clear()

        for i, page in enumerate(self._doc):
            pw = PDFPageWidget(page)
            pw.sig_rect_changed.connect(lambda r, idx=i: self.sig_rect_changed.emit(idx, r))
            self._layout.addWidget(pw)
            self._page_widgets.append(pw)
