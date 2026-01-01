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

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)
        if self.type == FinanceFileType.ZKB_CSV and not self.processed:
            from payment.parser import ZkbCsvParser
            from tq_website.tasks import match_payments

            ZkbCsvParser.parse_files_and_save_payments()
            # match payments immediately and after 2hrs to
            # allow for manual matching in between
            match_payments.apply_async(kwargs={"send_reminders": False})
            match_payments.apply_async(kwargs={"send_reminders": True}, countdown=3600)

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ["-created_at"]
