from .canvas import LabelCanvas
from .font_utils import load_font

FONT_HEADER_SIZE = 20
FONT_FIELD_SIZE = 18
FONT_MODEL_SIZE = 26
FONT_RIGHT_SIZE = 18


def _safe(value) -> str:
    if value is None:
        return ""
    return str(value)


def product_label(
    product_id: str,
    product_name: str,
    serial_no: str,
    release: str,
    stock_code: str,
    inspected_by: str,
    inspection_date: str,
    qr_text: str | None = None,
    order_no: str | None = None,
    width: int = 384,
    height: int = 240,
):
    product_id = _safe(product_id)
    product_name = _safe(product_name)
    serial_no = _safe(serial_no)
    release = _safe(release)
    stock_code = _safe(stock_code)
    inspected_by = _safe(inspected_by)
    inspection_date = _safe(inspection_date)
    order_no = _safe(order_no)

    canvas = LabelCanvas(width=width, height=height)

    font_header = load_font(FONT_HEADER_SIZE, bold=True)
    font_field = load_font(FONT_FIELD_SIZE, bold=True)
    font_model = load_font(FONT_MODEL_SIZE, bold=True)
    font_right = load_font(FONT_RIGHT_SIZE, bold=True)

    title = f"{product_id} - {product_name}"

    if qr_text is None:
        if order_no:
            qr_text = f"{product_id}|{stock_code}|{serial_no}|{release}|{order_no}"
        else:
            qr_text = f"{product_id}|{stock_code}|{serial_no}|{release}"

    # Header
    canvas.text_center(
        0,
        6,
        width,
        title,
        bold=True,
        font=font_header,
    )

    canvas.separator(y=30, x=10, w=width - 20, width=1)

    # Main info
    canvas.field(
        18,
        40,
        "SERIAL NO",
        serial_no,
        bold=True,
        font=font_field,
        label_width=120,
    )

    canvas.field(
        18,
        62,
        "RELEASE",
        release,
        bold=True,
        font=font_field,
        label_width=120,
    )

    if order_no:
        canvas.field(
            18,
            84,
            "ORDER NO",
            order_no,
            bold=True,
            font=font_field,
            label_width=120,
        )
        separator_y = 110
        qr_y = 122
        right_y0 = 128
    else:
        separator_y = 88
        qr_y = 102
        right_y0 = 110

    canvas.separator(y=separator_y, x=10, w=width - 20, width=1)

    # QR
    canvas.qrcode(
        18,
        qr_y,
        qr_text,
        box_size=3,
        border=2,
    )

    # Right side
    canvas.text(
        205,
        right_y0,
        stock_code,
        bold=True,
        font=font_model,
    )

    canvas.text(
        205,
        right_y0 + 45,
        "INSPECTED BY",
        bold=True,
        font=font_right,
    )

    canvas.text(
        205,
        right_y0 + 70,
        inspected_by,
        bold=True,
        font=font_right,
    )

    canvas.text(
        205,
        right_y0 + 95,
        inspection_date,
        bold=True,
        font=font_right,
    )

    return canvas.image


# from .canvas import LabelCanvas
# from .font_utils import load_font

# FONT_HEADER_SIZE = 20
# FONT_FIELD_SIZE = 18
# FONT_MODEL_SIZE = 26
# FONT_RIGHT_SIZE = 18


# def product_label(
#     product_id: str,
#     product_name: str,
#     serial_no: str,
#     release: str,
#     model_code: str,
#     inspected_by: str,
#     inspection_date: str,
#     qr_text: str | None = None,
#     width: int = 384,
#     height: int = 240,
# ):
#     canvas = LabelCanvas(width=width, height=height)

#     font_header = load_font(FONT_HEADER_SIZE, bold=True)
#     font_field = load_font(FONT_FIELD_SIZE, bold=True)
#     font_model = load_font(FONT_MODEL_SIZE, bold=True)
#     font_right = load_font(FONT_RIGHT_SIZE, bold=True)

#     title = f"{product_id} - {product_name}"

#     if qr_text is None:
#         qr_text = f"{model_code}|{serial_no}|{release}"

#     # --------------------------------------------------------
#     # Header
#     # --------------------------------------------------------

#     canvas.text_center(
#         0,
#         6,
#         width,
#         title,
#         bold=True,
#         font=font_header,
#     )

#     canvas.separator(y=30, x=10, w=width - 20, width=1)

#     # --------------------------------------------------------
#     # Device info
#     # --------------------------------------------------------

#     canvas.field(
#         18,
#         40,
#         "SERIAL NO",
#         serial_no,
#         bold=True,
#         font=font_field,
#         label_width=120,
#     )

#     canvas.field(
#         18,
#         62,
#         "RELEASE",
#         release,
#         bold=True,
#         font=font_field,
#         label_width=120,
#     )

#     canvas.separator(y=88, x=10, w=width - 20, width=1)

#     # --------------------------------------------------------
#     # QR Code
#     # --------------------------------------------------------

#     canvas.qrcode(
#         18,
#         102,
#         qr_text,
#         box_size=3,
#         border=2,
#     )

#     # --------------------------------------------------------
#     # Right side texts
#     # --------------------------------------------------------

#     canvas.text(
#         205,
#         110,
#         model_code,
#         bold=True,
#         font=font_model,
#     )

#     canvas.text(
#         205,
#         155,
#         "INSPECTED BY",
#         bold=True,
#         font=font_right,
#     )

#     canvas.text(
#         205,
#         180,
#         inspected_by,
#         bold=True,
#         font=font_right,
#     )

#     canvas.text(
#         205,
#         205,
#         inspection_date,
#         bold=True,
#         font=font_right,
#     )

#     return canvas.image


# def compression_testing_machine_label(
#     serial_no: str,
#     release: str,
#     model_code: str,
#     inspected_by: str,
#     inspection_date: str,
#     qr_text: str | None = None,
# ):
#     return product_label(
#         product_id="B001",
#         product_name="COMPRESSION TESTING MACHINE",
#         serial_no=serial_no,
#         release=release,
#         model_code=model_code,
#         inspected_by=inspected_by,
#         inspection_date=inspection_date,
#         qr_text=qr_text,
#     )
