# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import djangocms_text_ckeditor.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b"The name of this event (e.g. 'Freies Tanzen')", max_length=255)),
                ('date', models.DateField()),
                ('time_from', models.TimeField(null=True, blank=True)),
                ('time_to', models.TimeField(null=True, blank=True)),
                ('price_with_legi', models.FloatField(help_text=b'Leave this empty for free entrance', null=True, blank=True)),
                ('price_without_legi', models.FloatField(help_text=b'If this is a special event that should be emphasized on website', null=True, blank=True)),
                ('comment', models.TextField(null=True, blank=True)),
                ('description', djangocms_text_ckeditor.fields.HTMLField(null=True, blank=True)),
                ('special', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['date', 'time_from', 'room'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Organise',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('event', models.ForeignKey(related_name='organising', to='events.Event')),
                ('organiser', models.ForeignKey(related_name='organising', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='event',
            name='organisators',
            field=models.ManyToManyField(related_name='organising_events', through='events.Organise', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='room',
            field=models.ForeignKey(related_name='events', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='courses.Room', null=True),
            preserve_default=True,
        ),
    ]
