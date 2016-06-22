# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0031_course_evaluated'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('date', models.DateTimeField()),
                ('address', models.TextField(null=True, blank=True)),
                ('iban', models.CharField(max_length=34)),
                ('bic', models.CharField(max_length=11, null=True, blank=True)),
                ('amount', models.FloatField()),
                ('currency_code', models.CharField(max_length=3)),
                ('remittance_user_string', models.CharField(max_length=300)),
                ('state', models.CharField(max_length=20, choices=[(b'new', 'new'), (b'matched', 'matched'), (b'manual', 'manual'), (b'reimburse', 'reimburse'), (b'insufficient', 'insufficient payment'), (b'reimburse', 'reimburse')])),
                ('filename', models.CharField(max_length=300)),
                ('subscription', models.ForeignKey(blank=True, to='courses.Subscribe', null=True)),
            ],
        ),
    ]
