# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0032_auto_20160603_1123'),
        ('payment', '0002_auto_20160511_2211'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubscriptionPayment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.FloatField()),
            ],
        ),
        migrations.RemoveField(
            model_name='payment',
            name='subscription',
        ),
        migrations.AddField(
            model_name='payment',
            name='amount_to_reimburse',
            field=models.FloatField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='type',
            field=models.CharField(default=b'unknown', help_text=b'The type is auto-detected when the state is NEW, otherwise the detector will not touch this field anymore.', max_length=50, verbose_name=b'type (detected)', choices=[(b'subscription_payment', 'subscription payment'), (b'subscription_payment_to_reimburse', 'subscription payment (to reimburse)'), (b'course_payment_transfer', 'course payment transfer'), (b'irrelevant', 'irrelevant'), (b'unknown', 'unknown')]),
        ),
        migrations.AlterField(
            model_name='payment',
            name='state',
            field=models.CharField(default=b'new', max_length=50, choices=[(b'new', 'new'), (b'manual', 'manual'), (b'processed', 'processed')]),
        ),
        migrations.AddField(
            model_name='subscriptionpayment',
            name='payment',
            field=models.ForeignKey(related_name='subscription_payments', to='payment.Payment'),
        ),
        migrations.AddField(
            model_name='subscriptionpayment',
            name='subscription',
            field=models.ForeignKey(related_name='subscription_payments', to='courses.Subscribe'),
        ),
        migrations.AddField(
            model_name='payment',
            name='subscriptions',
            field=models.ManyToManyField(to='courses.Subscribe', through='payment.SubscriptionPayment', blank=True),
        ),
    ]
