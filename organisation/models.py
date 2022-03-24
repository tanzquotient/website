from cms.models import User
from django.db import models

from . import managers


class Function(models.Model):
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    email = models.EmailField(blank=True, null=True)
    users = models.ManyToManyField(User, blank=True, related_name='functions')

    # position field for ordering columns (grappelli feature)
    position = models.PositiveSmallIntegerField("Position", default=0)

    class Meta:
        ordering = ['position']

    objects = managers.FunctionManager()

    def format_users(self) -> str:
        return ', '.join(map(str, self.users.all()))

    format_users.short_description = "Usernames"

    def format_users_full_name(self) -> str:
        return ', '.join([user.get_full_name() for user in self.users.all()])

    format_users_full_name.short_description = "Users"

    def __str__(self) -> str:
        return "{}".format(self.name)
