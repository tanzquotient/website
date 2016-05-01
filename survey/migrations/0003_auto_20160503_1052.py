# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import parler.models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0002_auto_20160321_1610'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScaleTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(parler.models.TranslatableModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='ScaleTemplateTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language_code', models.CharField(max_length=15, verbose_name='Language', db_index=True)),
                ('low', models.CharField(max_length=30)),
                ('mid', models.CharField(max_length=30, null=True, blank=True)),
                ('up', models.CharField(max_length=30)),
                ('master', models.ForeignKey(related_name='translations', editable=False, to='survey.ScaleTemplate', null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'survey_scaletemplate_translation',
                'db_tablespace': '',
                'default_permissions': (),
                'verbose_name': 'scale template Translation',
            },
        ),
        migrations.AlterModelOptions(
            name='choicetranslation',
            options={'default_permissions': (), 'verbose_name': 'choice Translation', 'managed': True},
        ),
        migrations.AlterModelOptions(
            name='questiongrouptranslation',
            options={'default_permissions': (), 'verbose_name': 'question group Translation', 'managed': True},
        ),
        migrations.AlterModelOptions(
            name='questiontranslation',
            options={'default_permissions': (), 'verbose_name': 'question Translation', 'managed': True},
        ),
        migrations.AlterModelOptions(
            name='surveytranslation',
            options={'default_permissions': (), 'verbose_name': 'survey Translation', 'managed': True},
        ),
        migrations.AlterField(
            model_name='answer',
            name='choice',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='survey.Choice', null=True),
        ),
        migrations.AlterField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(related_name='answers', on_delete=django.db.models.deletion.SET_NULL, to='survey.Question', null=True),
        ),
        migrations.AlterField(
            model_name='choicetranslation',
            name='language_code',
            field=models.CharField(max_length=15, verbose_name='Language', db_index=True),
        ),
        migrations.AlterField(
            model_name='question',
            name='type',
            field=models.CharField(default=b'f', max_length=3, choices=[(b'c', 'single choice'), (b'cf', 'single choice with free form'), (b'm', 'multiple choice'), (b'mf', 'multiple choice with free form'), (b's', 'scale'), (b'f', 'free form')]),
        ),
        migrations.AlterField(
            model_name='questiongrouptranslation',
            name='language_code',
            field=models.CharField(max_length=15, verbose_name='Language', db_index=True),
        ),
        migrations.AlterField(
            model_name='questiontranslation',
            name='language_code',
            field=models.CharField(max_length=15, verbose_name='Language', db_index=True),
        ),
        migrations.AlterField(
            model_name='surveytranslation',
            name='language_code',
            field=models.CharField(max_length=15, verbose_name='Language', db_index=True),
        ),
        migrations.AddField(
            model_name='question',
            name='scale_template',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='survey.ScaleTemplate', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='scaletemplatetranslation',
            unique_together=set([('language_code', 'master')]),
        ),
    ]
