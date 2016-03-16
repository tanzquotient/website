# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField(null=True, blank=True)),
                ('value', models.IntegerField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Choice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.PositiveSmallIntegerField(default=0, verbose_name=b'Position')),
            ],
            options={
                'ordering': ['position'],
            },
        ),
        migrations.CreateModel(
            name='ChoiceTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=255)),
                ('language_code', models.CharField(max_length=15, db_index=True)),
                ('master', models.ForeignKey(related_name='translations', editable=False, to='survey.Choice', null=True)),
            ],
            options={
                'managed': True,
                'abstract': False,
                'db_table': 'survey_choice_translation',
                'db_tablespace': '',
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('type', models.CharField(default=b'c', max_length=3, choices=[(b'c', 'single choice'), (b'm', 'multiple choice'), (b's', 'scale'), (b'f', 'free form')])),
                ('display', models.BooleanField(default=True, help_text=b'Defines if this question is displayed in survey; set this to false instead of deleting')),
                ('position', models.PositiveSmallIntegerField(default=0, verbose_name=b'Position')),
            ],
            options={
                'ordering': ['position'],
            },
        ),
        migrations.CreateModel(
            name='QuestionGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('position', models.PositiveSmallIntegerField(default=0, verbose_name=b'Position')),
            ],
            options={
                'ordering': ['position'],
            },
        ),
        migrations.CreateModel(
            name='QuestionGroupTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('intro_text', models.TextField(null=True, blank=True)),
                ('language_code', models.CharField(max_length=15, db_index=True)),
                ('master', models.ForeignKey(related_name='translations', editable=False, to='survey.QuestionGroup', null=True)),
            ],
            options={
                'managed': True,
                'abstract': False,
                'db_table': 'survey_questiongroup_translation',
                'db_tablespace': '',
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='QuestionTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField(null=True, blank=True)),
                ('note', models.TextField(null=True, blank=True)),
                ('language_code', models.CharField(max_length=15, db_index=True)),
                ('master', models.ForeignKey(related_name='translations', editable=False, to='survey.Question', null=True)),
            ],
            options={
                'managed': True,
                'abstract': False,
                'db_table': 'survey_question_translation',
                'db_tablespace': '',
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SurveyTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('intro_text', models.TextField(null=True, blank=True)),
                ('language_code', models.CharField(max_length=15, db_index=True)),
                ('master', models.ForeignKey(related_name='translations', editable=False, to='survey.Survey', null=True)),
            ],
            options={
                'managed': True,
                'abstract': False,
                'db_table': 'survey_survey_translation',
                'db_tablespace': '',
                'default_permissions': (),
            },
        ),
        migrations.AddField(
            model_name='questiongroup',
            name='survey',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='survey.Survey', null=True),
        ),
        migrations.AddField(
            model_name='question',
            name='question_group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='survey.QuestionGroup', null=True),
        ),
        migrations.AddField(
            model_name='choice',
            name='question',
            field=models.ForeignKey(to='survey.Question', null=True),
        ),
        migrations.AddField(
            model_name='answer',
            name='choice',
            field=models.ForeignKey(to='survey.Question', null=True),
        ),
        migrations.AddField(
            model_name='answer',
            name='user',
            field=models.ForeignKey(related_name='survey_answers', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='surveytranslation',
            unique_together=set([('language_code', 'master')]),
        ),
        migrations.AlterUniqueTogether(
            name='questiontranslation',
            unique_together=set([('language_code', 'master')]),
        ),
        migrations.AlterUniqueTogether(
            name='questiongrouptranslation',
            unique_together=set([('language_code', 'master')]),
        ),
        migrations.AlterUniqueTogether(
            name='choicetranslation',
            unique_together=set([('language_code', 'master')]),
        ),
    ]
