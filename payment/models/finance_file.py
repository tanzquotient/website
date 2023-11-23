from django.db.models import BooleanField, CharField, FileField, DateTimeField, Model

from payment.models.choices import FinanceFileType
from tq_website.storages import FinanceStorage


class FinanceFile(Model):
    name = CharField(max_length=200, unique=True)
    file = FileField(storage=FinanceStorage())
    type = CharField(
        max_length=32,
        choices=FinanceFileType.CHOICES,
        default=FinanceFileType.ZKB_CSV,
    )
    processed = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ) -> None:
        super().save(force_insert, force_update, using, update_fields)
        if self.type == FinanceFileType.ZKB_CSV and not self.processed:
            from payment.parser import ZkbCsvParser

            ZkbCsvParser.parse_files_and_save_payments()

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ["-created_at"]
