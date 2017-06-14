from django.db import models

from django.conf import settings

from . import managers


# Create your models here.
class Function(models.Model):
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    email = models.EmailField(blank=True, null=True)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='functions')

    # position field for ordering columns (grappelli feature)
    position = models.PositiveSmallIntegerField("Position", default=0)

    class Meta:
        ordering = ['position']

    objects = managers.FunctionManager()

    def format_users(self):
        return ', '.join(map(str, self.users.all()))

    format_users.short_description = "Usernames"

    def format_users_full_name(self):
        return ', '.join([user.get_full_name() for user in self.users.all()])

    format_users_full_name.short_description = "Users"

    def __str__(self):
        return "{}".format(self.name)
