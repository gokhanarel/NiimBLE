from PIL import Image, ImageDraw


class LabelCanvas:
    def __init__(
        self,
        width: int = 384,
        height: int = 240,
        background: int = 1,
    ):
        self.width = width
        self.height = height
        self.image = Image.new("1", (width, height), background)
        self.draw = ImageDraw.Draw(self.image)

    # ------------------------------------------------------------
    # Basic helpers
    # ------------------------------------------------------------

    def clear(self, color: int = 1):
        self.draw.rectangle((0, 0, self.width, self.height), fill=color)

    def save(self, filename: str):
        self.image.save(filename)

    def show(self):
        self.image.show()

    # ------------------------------------------------------------
    # Lines / shapes
    # ------------------------------------------------------------

    def line(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        width: int = 1,
        fill: int = 0,
    ):
        self.draw.line((x1, y1, x2, y2), fill=fill, width=width)

    def hline(
        self,
        x: int,
        y: int,
        w: int,
        width: int = 1,
        fill: int = 0,
    ):
        self.draw.line((x, y, x + w - 1, y), fill=fill, width=width)

    def vline(
        self,
        x: int,
        y: int,
        h: int,
        width: int = 1,
        fill: int = 0,
    ):
        self.draw.line((x, y, x, y + h - 1), fill=fill, width=width)

    def separator(
        self,
        y: int,
        x: int = 5,
        w: int | None = None,
        width: int = 1,
        fill: int = 0,
    ):
        if w is None:
            w = self.width - 2 * x

        self.hline(x, y, w, width=width, fill=fill)

    def rect(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        outline: int = 0,
        width: int = 1,
    ):
        self.draw.rectangle(
            (x, y, x + w - 1, y + h - 1),
            outline=outline,
            width=width,
        )

    def filled_rect(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        fill: int = 0,
    ):
        self.draw.rectangle(
            (x, y, x + w - 1, y + h - 1),
            fill=fill,
        )

    # ------------------------------------------------------------
    # Text helpers
    # ------------------------------------------------------------

    def text_width(self, text: str, font=None) -> int:
        bbox = self.draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0]

    def text_height(self, text: str, font=None) -> int:
        bbox = self.draw.textbbox((0, 0), text, font=font)
        return bbox[3] - bbox[1]

    def text(
        self,
        x: int,
        y: int,
        text: str,
        fill: int = 0,
        bold: bool = False,
        font=None,
    ):
        self.draw.text((x, y), text, fill=fill, font=font)

        if bold:
            self.draw.text((x + 1, y), text, fill=fill, font=font)

    def text_center(
        self,
        x: int,
        y: int,
        w: int,
        text: str,
        fill: int = 0,
        bold: bool = False,
        font=None,
    ):
        text_w = self.text_width(text, font=font)
        draw_x = x + (w - text_w) // 2
        self.text(draw_x, y, text, fill=fill, bold=bold, font=font)

    def text_right(
        self,
        x: int,
        y: int,
        w: int,
        text: str,
        fill: int = 0,
        bold: bool = False,
        font=None,
    ):
        text_w = self.text_width(text, font=font)
        draw_x = x + w - text_w
        self.text(draw_x, y, text, fill=fill, bold=bold, font=font)

    def field(
        self,
        x: int,
        y: int,
        label: str,
        value: str,
        fill: int = 0,
        bold: bool = False,
        font=None,
        label_width: int | None = None,
    ):
        label = label or ""
        value = value or ""

        if label_width is None:
            text = f"{label}: {value}"
            self.text(x, y, text, fill=fill, bold=bold, font=font)
            return

        self.text(x, y, label, fill=fill, bold=bold, font=font)
        self.text(x + label_width, y, ": ", fill=fill, bold=bold, font=font)
        self.text(x + label_width + 18, y, value, fill=fill, bold=bold, font=font)

    def multiline_text(
        self,
        x: int,
        y: int,
        lines: list[str],
        line_height: int = 22,
        fill: int = 0,
        bold: bool = False,
        font=None,
    ):
        for i, line in enumerate(lines):
            self.text(
                x,
                y + i * line_height,
                line,
                fill=fill,
                bold=bold,
                font=font,
            )

    # ------------------------------------------------------------
    # QR Code
    # ------------------------------------------------------------

    def qrcode(
        self,
        x: int,
        y: int,
        text: str,
        box_size: int = 3,
        border: int = 2,
        invert: bool = False,
    ) -> int:
        try:
            import qrcode
        except ImportError as exc:
            raise ImportError(
                "QR code support requires qrcode package. Install with: pip install qrcode[pil]"
            ) from exc

        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=box_size,
            border=border,
        )

        qr.add_data(text)
        qr.make(fit=True)

        qr_img = qr.make_image(fill_color="black", back_color="white").convert("1")

        if invert:
            qr_img = qr_img.point(lambda p: 0 if p else 255)

        self.image.paste(qr_img, (x, y))

        return qr_img.size[0]

    def qrcode_center(
        self,
        x: int,
        y: int,
        w: int,
        text: str,
        box_size: int = 4,
        border: int = 2,
    ) -> int:
        try:
            import qrcode
        except ImportError as exc:
            raise ImportError(
                "QR code support requires qrcode package. Install with: pip install qrcode[pil]"
            ) from exc

        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=box_size,
            border=border,
        )

        qr.add_data(text)
        qr.make(fit=True)

        qr_img = qr.make_image(fill_color="black", back_color="white").convert("1")

        draw_x = x + (w - qr_img.size[0]) // 2
        self.image.paste(qr_img, (draw_x, y))

        return qr_img.size[0]
