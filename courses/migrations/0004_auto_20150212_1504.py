# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0003_auto_20150211_0923'),
    ]

    operations = [
        migrations.CreateModel(
            name='Confirmation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(help_text=b'The date when the participation confirmation mail was sent to the subscriber.', auto_now_add=True)),
                ('subscription', models.ForeignKey(related_name='confirmations', to='courses.Subscribe')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='subscribe',
            name='confirmed',
            field=models.BooleanField(default=False, help_text=b'When this is checked, a participation confirmation email is send (once) to the user while saving this form.'),
            preserve_default=True,
        ),
    ]
