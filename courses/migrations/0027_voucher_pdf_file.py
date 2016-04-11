# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0026_auto_20160405_1337'),
    ]

    operations = [
        migrations.AddField(
            model_name='voucher',
            name='pdf_file',
            field=models.FileField(null=True, upload_to=b'media/', blank=True),
        ),
    ]
