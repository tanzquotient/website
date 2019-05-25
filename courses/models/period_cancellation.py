from django.db import models


class PeriodCancellation(models.Model):
    period = models.ForeignKey('Period', related_name='cancellations', on_delete=models.CASCADE)
    date = models.DateField(blank=False, null=True)

    def __str__(self):
        return "{}".format(self.date.strftime('%d.%m.%Y'))
