# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import djangocms_text_ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_auto_20150209_1113'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='description',
            field=djangocms_text_ckeditor.fields.HTMLField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
