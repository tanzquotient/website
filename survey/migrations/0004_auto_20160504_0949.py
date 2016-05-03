# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0031_course_evaluated'),
        ('survey', '0003_auto_20160503_1052'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='answer',
            name='value',
        ),
        migrations.RemoveField(
            model_name='surveyinstance',
            name='courses',
        ),
        migrations.AddField(
            model_name='surveyinstance',
            name='course',
            field=models.ForeignKey(related_name='survey_instances', blank=True, to='courses.Course', null=True),
        ),
        migrations.AddField(
            model_name='surveyinstance',
            name='invitation_sent',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='surveyinstance',
            name='last_update',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
