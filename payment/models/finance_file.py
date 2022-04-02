from django.db.models import BooleanField, CharField, FileField, DateTimeField, Model

from payment.models.choices import FinanceFileType
from tq_website.storages import FinanceStorage


class FinanceFile(Model):
    name = CharField(max_length=200, unique=True)
    file = FileField(storage=FinanceStorage())
    type = CharField(max_length=32, choices=FinanceFileType.CHOICES, default=FinanceFileType.POSTFINANCE_XML)
    processed = BooleanField(default=False)
    downloaded_at = DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ['-downloaded_at']
