# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0017_fix_subscribe_matching_state'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rejection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(help_text=b'The date when the rejection mail was sent to the subscriber.', auto_now_add=True)),
                ('reason', models.CharField(default=b'unknown', max_length=30, choices=[(b'unknown', 'Unknown'), (b'overbooked', 'Overbooked'), (b'no_partner', 'No partner found')])),
                ('subscription', models.ForeignKey(related_name='rejections', to='courses.Subscribe')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='subscribe',
            name='rejected',
            field=models.BooleanField(default=False, help_text=b'When this is checked, a rejection email is send (once) to the user while saving this form.'),
            preserve_default=True,
        ),
    ]
