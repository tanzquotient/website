from tempfile import TemporaryFile

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from courses.models import Subscribe
from payment.utils import create_qrbill_for_subscription, to_pdf

def subscription_qr_bill_export_pdf(request: HttpRequest, usi: str):
    subscription = get_object_or_404(Subscribe, usi=usi)
    
    with TemporaryFile() as pdf_file:
        to_pdf(create_qrbill_for_subscription(subscription), pdf_file)
        length = pdf_file.tell()
        pdf_file.seek(0)
        response = HttpResponse(pdf_file, content_type="application/pdf")
        response["Content-Disposition"] = f"attachment; filename=QR-bill_{usi}.pdf"
        response["Content-Length"] = length
        return response