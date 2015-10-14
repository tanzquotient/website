# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0018_auto_20150920_1901'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coursetype',
            name='styles',
            field=models.ManyToManyField(related_name='course_types', to='courses.Style', blank=True),
        ),
        migrations.AlterField(
            model_name='musicpluginmodel',
            name='styles',
            field=models.ManyToManyField(help_text='Styles to be displayed in this plugin. Leave empty to show all styles.', to='courses.Style', blank=True),
        ),
    ]
