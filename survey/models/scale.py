from django.db.models import CharField
from parler.models import TranslatableModel, TranslatedFields


class Scale(TranslatableModel):
    translations = TranslatedFields(
        low=CharField(verbose_name='[TR] Text for lower', max_length=30),
        up=CharField(verbose_name='[TR] Text for upper', max_length=30)
    )

    def __str__(self) -> str:
        return f"{self.low} - {self.up}"
