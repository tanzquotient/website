# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('courses', '0021_auto_20160220_1828'),
        ('survey', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SurveyInstance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('url_text', models.CharField(unique=True, max_length=100, blank=True)),
                ('url_checksum', models.CharField(max_length=12, blank=True)),
                ('url_expire_date', models.DateTimeField(null=True, blank=True)),
                ('courses', models.ManyToManyField(related_name='survey_instances', to='courses.Course', blank=True)),
                ('survey', models.ForeignKey(related_name='survey_instances', to='survey.Survey')),
                ('user', models.ForeignKey(related_name='survey_instances', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='answer',
            name='user',
        ),
        migrations.AddField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(related_name='answers', to='survey.Question', null=True),
        ),
        migrations.AlterField(
            model_name='answer',
            name='choice',
            field=models.ForeignKey(blank=True, to='survey.Question', null=True),
        ),
        migrations.AlterField(
            model_name='question',
            name='type',
            field=models.CharField(default=b'c', max_length=3, choices=[(b'c', 'single choice'), (b'cf', 'single choice with free form'), (b'm', 'multiple choice'), (b'mf', 'multiple choice with free form'), (b's', 'scale'), (b'f', 'free form')]),
        ),
        migrations.AddField(
            model_name='answer',
            name='survey_instance',
            field=models.ForeignKey(related_name='answers', to='survey.SurveyInstance', null=True),
        ),
    ]
