from io import StringIO, BytesIO
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from tempfile import TemporaryFile

from qrbill import QRBill
from qrbill.bill import StructuredAddress

import qrcode

from tq_website import settings

from courses.models import Subscribe


def create_qrbill_for_subscription(subscribe: Subscribe) -> QRBill:
    payment_account = settings.PAYMENT_ACCOUNT["default"]
    postal_code, city = payment_account["postal_code_and_city"].split(" ")
    return QRBill(
        account=payment_account["IBAN"],
        creditor=dict(
            name=payment_account["recipient_name"], pcode=postal_code, city=city
        ),
        amount=str(subscribe.open_amount()),
        additional_information=f"USI-{subscribe.usi}",
        top_line=False,
        payment_line=False,
    )


def to_svg_string(qr_bill: QRBill, qr_only: bool = False) -> str:
    if qr_only:
        return qrcode.make(
            qr_bill.qr_data(),
            image_factory=qrcode.image.svg.SvgPathFillImage,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            border=1,
        ).to_string(encoding="unicode")

    else:
        with StringIO() as file:
            qr_bill.as_svg(file)
            return file.getvalue()


def to_pdf(qr_bill: QRBill, pdf_file) -> None:
    with TemporaryFile(encoding="utf-8", mode="r+") as temp:
        qr_bill.as_svg(temp)
        temp.seek(0)
        drawing = svg2rlg(temp)

    renderPDF.drawToFile(drawing, pdf_file)
