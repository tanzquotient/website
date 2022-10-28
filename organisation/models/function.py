from cms.models import User
from django.db.models import EmailField, ManyToManyField, CharField
from parler.models import TranslatableModel, TranslatedFields


class Function(TranslatableModel):
    email = EmailField(blank=True, null=True)
    users = ManyToManyField(User, blank=True, related_name='functions')

    translations = TranslatedFields(
        name=CharField(
            verbose_name='[TR] Name', max_length=64, blank=False,
            help_text="The name of the ressort. E.g. Event Management")
    )

    class Meta:
        ordering = ['email']

    def names(self) -> str:
        return ', '.join([user.get_full_name() for user in self.users.all()])

    def __str__(self) -> str:
        return f"{self.name}: {self.names()}"
