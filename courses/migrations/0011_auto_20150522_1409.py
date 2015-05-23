# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0010_auto_20150416_1639'),
    ]

    operations = [
        migrations.CreateModel(
            name='IrregularLesson',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField()),
                ('time_from', models.TimeField()),
                ('time_to', models.TimeField()),
                ('course', models.ForeignKey(related_name='irregular_lessons', to='courses.Course')),
                ('room', models.ForeignKey(related_name='irregular_lessons', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='courses.Room', help_text=b'The room for this lesson. If left empty, the course room is assumed.', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RenameModel(
            old_name='CourseTime',
            new_name='RegularLesson',
        ),
        migrations.AlterField(
            model_name='RegularLesson',
            name='course',
            field=models.ForeignKey(related_name='regular_lessons', to='courses.Course'),
            preserve_default=True,
        ),
        migrations.RenameModel(
            old_name='CourseCancellation',
            new_name='RegularLessonCancellation',
        ),
        migrations.AddField(
            model_name='offering',
            name='type',
            field=models.CharField(default=b'reg', help_text=b'The type of the offering influences how the offering is displayed.', max_length=3, choices=[(b'reg', 'Regular (weekly)'), (b'irr', 'Irregular (Workshops)')]),
            preserve_default=True,
        ),
    ]
