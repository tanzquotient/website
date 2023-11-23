from __future__ import unicode_literals

import os
from io import open
from tempfile import gettempdir
from typing import Iterable, Optional

from django.conf import settings
from django.contrib import admin
from django.core.files.base import ContentFile
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg

from courses.models import Voucher


def _get_voucher_template() -> str:
    template_file = os.path.join(settings.BASE_DIR, "payment", "Voucher.svg")
    with open(template_file, encoding="utf-8") as file:
        template_content = file.read()
        return template_content


def generate_voucher_pdf(
    voucher: Voucher, template_content: Optional[str] = None
) -> ContentFile:
    filename = "Voucher-" + voucher.key + ".pdf"

    issued = voucher.issued.strftime("%d.%m.%Y")
    expires = voucher.expires.strftime("%d.%m.%Y") if voucher.expires else "never"

    if template_content is None:
        template_content = _get_voucher_template()

    content = (
        template_content.replace("{{ issued }}", issued)
        .replace("{{ expires }}", expires)
        .replace("{{ code }}", voucher.key)
        .replace("{{ value }}", voucher.value_string())
    )
    tmpdir = gettempdir()
    temp_path = os.path.join(tmpdir, "voucher.svg")
    with open(temp_path, mode="wb") as temp_file:
        temp_file.write(content.encode("utf-8"))

    drawing = svg2rlg(temp_path)
    path = os.path.join(tmpdir, filename)
    renderPDF.drawToFile(drawing, path)
    with open(path, "r", encoding="latin-1") as file:
        content = file.read()

    return ContentFile(content.encode("utf-8"), name=filename)


def generate_voucher_pdfs(vouchers: Iterable[Voucher]) -> None:
    template_content = _get_voucher_template()

    for voucher in vouchers:
        generated_file = generate_voucher_pdf(voucher, template_content)
        voucher.pdf_file.save(generated_file.name, generated_file)
