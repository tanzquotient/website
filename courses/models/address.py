from django.db import models
from django_countries.fields import CountryField

from courses import managers


class Address(models.Model):
    street = models.CharField(max_length=255)
    plz = models.IntegerField()
    city = models.CharField(max_length=255)
    country = CountryField(default="CH")

    objects = managers.AddressManager()

    def equals(self, a):
        return self.street == a.street and self.plz == a.plz and self.city == a.city

    def __str__(self) -> str:
        return f"{self.street}, {self.plz} {self.city}{f', {self.country}' if self.country != 'CH' else ''}"
