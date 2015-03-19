# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import djangocms_text_ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0006_userprofile_body_height'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='about_me',
            field=djangocms_text_ckeditor.fields.HTMLField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
