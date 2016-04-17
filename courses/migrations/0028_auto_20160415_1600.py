# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0027_voucher_pdf_file'),
    ]

    operations = [
        migrations.RenameField(
            model_name='subscribe',
            old_name='status',
            new_name='state',
        ),
        migrations.AlterField(
            model_name='voucher',
            name='pdf_file',
            field=models.FileField(null=True, upload_to=b'/voucher/', blank=True),
        ),
    ]
