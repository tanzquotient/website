# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import djangocms_text_ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0008_musicpluginmodel'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='comment',
        ),
        migrations.AddField(
            model_name='course',
            name='open_class',
            field=models.BooleanField(default=False, help_text=b'Open classes do not require a subscription or subscription is done via a different channel.'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='course',
            name='price_special',
            field=models.CharField(help_text='Set this only if you want a different price schema.', max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='course',
            name='special',
            field=djangocms_text_ckeditor.fields.HTMLField(help_text=b'Any special properties of this course.', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='coursetype',
            name='description',
            field=djangocms_text_ckeditor.fields.HTMLField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='period',
            name='date_from',
            field=models.DateField(help_text='The start date of this period. Can be left empty.', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='period',
            name='date_to',
            field=models.DateField(help_text="The end date of this period. Can be left empty. If both are left empty, this period is displayed as 'on request'.", null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='room',
            name='description',
            field=djangocms_text_ckeditor.fields.HTMLField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='style',
            name='description',
            field=djangocms_text_ckeditor.fields.HTMLField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
