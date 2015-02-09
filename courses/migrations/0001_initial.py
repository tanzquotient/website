# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tinymce.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('street', models.CharField(max_length=255)),
                ('plz', models.IntegerField()),
                ('city', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'This name is just for reference and is not displayed anywhere on the website.', max_length=255)),
                ('min_subscribers', models.IntegerField(default=6)),
                ('max_subscribers', models.IntegerField(null=True, blank=True)),
                ('price_with_legi', models.FloatField(default=35, null=True, blank=True)),
                ('price_without_legi', models.FloatField(default=70, null=True, blank=True)),
                ('comment', models.TextField(null=True, blank=True)),
                ('position', models.PositiveSmallIntegerField(default=0, verbose_name=b'Position')),
            ],
            options={
                'ordering': ['position'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CourseCancellation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(null=True)),
                ('course', models.ForeignKey(related_name='cancellations', to='courses.Course')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CourseTime',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('weekday', models.CharField(default=None, max_length=3, choices=[(b'mon', 'Monday'), (b'tue', 'Tuesday'), (b'wed', 'Wednesday'), (b'thu', 'Thursday'), (b'fri', 'Friday'), (b'sat', 'Saturday'), (b'sun', 'Sunday')])),
                ('time_from', models.TimeField()),
                ('time_to', models.TimeField()),
                ('course', models.ForeignKey(related_name='times', to='courses.Course')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CourseType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=30)),
                ('level', models.IntegerField(default=None, null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('special', models.TextField(null=True, blank=True)),
                ('couple_course', models.BooleanField(default=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Offering',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=30)),
                ('display', models.BooleanField(default=False, help_text=b'Defines if the courses in this offering should be displayed on the Website.')),
                ('active', models.BooleanField(default=False, help_text=b'Defines if clients can subscribe to courses in this offering.')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Period',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_from', models.DateField()),
                ('date_to', models.DateField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PeriodCancellation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(null=True)),
                ('course', models.ForeignKey(related_name='cancellations', to='courses.Period')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=30)),
                ('description', models.TextField(null=True, blank=True)),
                ('url', models.URLField(help_text=b'The url to Google Maps (see https://support.google.com/maps/answer/144361?p=newmaps_shorturl&rd=1)', max_length=500, null=True, blank=True)),
                ('contact_info', models.TextField(null=True, blank=True)),
                ('address', models.OneToOneField(null=True, blank=True, to='courses.Address')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Song',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('artist', models.CharField(max_length=255, null=True, blank=True)),
                ('length', models.TimeField(null=True, blank=True)),
                ('speed', models.IntegerField(help_text=b'The speed of the song in TPM', null=True, blank=True)),
                ('url_video', models.URLField(help_text=b'A url to a demo video (e.g Youtube).', max_length=500, null=True, blank=True)),
            ],
            options={
                'ordering': ['speed', 'length'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Style',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=30)),
                ('description', models.TextField(null=True, blank=True)),
                ('url_info', models.URLField(help_text=b'A url to an information page (e.g. Wikipedia).', max_length=500, null=True, blank=True)),
                ('url_video', models.URLField(help_text=b'A url to a demo video (e.g Youtube).', max_length=500, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Subscribe',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(help_text=b'The date when the subscription was made.', auto_now_add=True)),
                ('experience', models.TextField(null=True, blank=True)),
                ('comment', models.TextField(help_text=b'A optional comment made by the user during subscription.', null=True, blank=True)),
                ('confirmed', models.BooleanField(default=False, help_text=b'When this is checked, a confirmation email is send (once) to the user while saving this form.')),
                ('payed', models.BooleanField(default=False)),
                ('course', models.ForeignKey(related_name='subscriptions', to='courses.Course')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Teach',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('course', models.ForeignKey(related_name='teaching', to='courses.Course')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('user', models.OneToOneField(related_name='profile', primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL, help_text=b'The user which is matched to this user profile.')),
                ('legi', models.CharField(max_length=16, null=True, blank=True)),
                ('gender', models.CharField(default=None, max_length=1, null=True, choices=[(b'm', 'Men'), (b'w', 'Woman')])),
                ('phone_number', models.CharField(max_length=255, null=True, blank=True)),
                ('student_status', models.CharField(default=b'no', max_length=10, choices=[(b'eth', 'ETH'), (b'uni', 'Uni'), (b'ph', 'PH'), (b'other', 'Other'), (b'no', 'Not a student')])),
                ('newsletter', models.BooleanField(default=True)),
                ('about_me', tinymce.models.HTMLField(null=True, blank=True)),
                ('address', models.OneToOneField(null=True, blank=True, to='courses.Address')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='teach',
            name='teacher',
            field=models.ForeignKey(related_name='teaching', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='subscribe',
            name='partner',
            field=models.ForeignKey(related_name='subscriptions_as_partner', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='subscribe',
            name='user',
            field=models.ForeignKey(related_name='subscriptions', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='song',
            name='style',
            field=models.ForeignKey(related_name='songs', on_delete=django.db.models.deletion.SET_NULL, to='courses.Style', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='offering',
            name='period',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='courses.Period', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='coursetype',
            name='styles',
            field=models.ManyToManyField(related_name='course_types', null=True, to='courses.Style', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='course',
            name='offering',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='courses.Offering', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='course',
            name='period',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='courses.Period', help_text=b'You can set a custom period for this course here. If this is left empty, the period from the offering is taken.', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='course',
            name='room',
            field=models.ForeignKey(related_name='courses', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='courses.Room', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='course',
            name='subscribers',
            field=models.ManyToManyField(related_name='courses', through='courses.Subscribe', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='course',
            name='teachers',
            field=models.ManyToManyField(related_name='teaching_courses', through='courses.Teach', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='course',
            name='type',
            field=models.ForeignKey(related_name='courses', to='courses.CourseType', help_text=b'The name of the course type is displayed on the website as the course title .'),
            preserve_default=True,
        ),
    ]
