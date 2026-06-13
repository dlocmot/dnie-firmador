"""Render the Refirma-compatible visual signature stamp."""

from __future__ import annotations

import io
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ASSETS_DIR = Path(__file__).parent.parent / "assets"
DEFAULT_SHIELD = ASSETS_DIR / "escudo.svg"

# Stamp dimensions in points (1 pt = 1/72 inch)
STAMP_WIDTH = 280
STAMP_HEIGHT = 80
BORDER_COLOR = (180, 0, 0)  # red
BORDER_WIDTH = 2
FONT_SIZE_LABEL = 7
FONT_SIZE_BODY = 8


@dataclass
class SignatureAppearance:
    """All configurable parameters for the visual signature stamp."""

    signer_name: str
    dni: str
    reason: str = "Soy el autor del documento"
    image_path: Path = field(default_factory=lambda: DEFAULT_SHIELD)
    label_text: str = "FIRMA\nDIGITAL"
    width_pt: int = STAMP_WIDTH
    height_pt: int = STAMP_HEIGHT

    def render_png(self, timestamp: str) -> bytes:
        """Render the stamp to PNG bytes at 150 dpi."""
        dpi = 150
        scale = dpi / 72
        w = int(self.width_pt * scale)
        h = int(self.height_pt * scale)

        img = Image.new("RGB", (w, h), "white")
        draw = ImageDraw.Draw(img)

        # Red border
        bw = max(1, int(BORDER_WIDTH * scale))
        draw.rectangle([0, 0, w - 1, h - 1], outline=BORDER_COLOR, width=bw)

        # Left section: image + label
        img_w = int(h * 0.55)
        self._draw_left(img, draw, img_w, h, scale)

        # Divider
        draw.line([(img_w + bw, bw), (img_w + bw, h - bw)], fill=BORDER_COLOR, width=bw)

        # Right section: text block
        self._draw_right(draw, img_w + bw * 2, w, h, timestamp, scale)

        buf = io.BytesIO()
        img.save(buf, format="PNG", dpi=(dpi, dpi))
        return buf.getvalue()

    def _draw_left(self, img: Image.Image, draw: ImageDraw.Draw, img_w: int, h: int, scale: float):
        try:
            from cairosvg import svg2png
            png_data = svg2png(url=str(self.image_path), output_width=img_w - 8, output_height=h - 24)
            shield = Image.open(io.BytesIO(png_data)).convert("RGBA")
            img.paste(shield, (4, 4), shield)
        except Exception:
            draw.text((4, 4), "[img]", fill="gray")

        label_font = self._font(int(FONT_SIZE_LABEL * scale * 0.9))
        draw.text((4, h - int(14 * scale)), self.label_text, font=label_font, fill=BORDER_COLOR)

    def _draw_right(self, draw: ImageDraw.Draw, x: int, w: int, h: int, timestamp: str, scale: float):
        font = self._font(int(FONT_SIZE_BODY * scale))
        lines = [
            "Firmado digitalmente por:",
            f"{self.signer_name} {self.dni} hard",
            f"Motivo: {self.reason}",
            f"Fecha: {timestamp}",
        ]
        y = int(6 * scale)
        line_h = int(11 * scale)
        for line in lines:
            draw.text((x + 4, y), line, font=font, fill="black")
            y += line_h

    @staticmethod
    def _font(size: int):
        try:
            return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
        except Exception:
            return ImageFont.load_default()
