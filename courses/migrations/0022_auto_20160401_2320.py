# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def populate_status(apps, schema_editor):
    Subscribe = apps.get_model("courses", "Subscribe")
    for s in Subscribe.objects.all():
        if s.rejected:
            s.status = "rejected"
        elif s.confirmed:
            if s.payed:
                s.status = "completed"
            else:
                s.status = "confirmed"

def populate_usi(apps, schema_editor):
    Subscribe = apps.get_model("courses", "Subscribe")
    for s in Subscribe.objects.all():
        s.generate_usi()



class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0021_auto_20160220_1828'),
    ]

    operations = [
        migrations.CreateModel(
            name='Voucher',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(unique=True, max_length=8)),
                ('issued', models.DateField(auto_now_add=True)),
                ('expires', models.DateField(null=True, blank=True)),
                ('used', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['issued', 'expires'],
            },
        ),
        migrations.CreateModel(
            name='VoucherPurpose',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('description', models.TextField(null=True, blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='subscribe',
            name='status',
            field=models.CharField(default=b'new', max_length=30, choices=[(b'new', 'new'), (b'confirmed', 'confirmed (to pay)'), (b'payed', 'payed'), (b'completed', 'completed'), (b'rejected', 'rejected'), (b'to_reimburse', 'to reimburse')]),
        ),
        migrations.AddField(
            model_name='subscribe',
            name='usi',
            field=models.CharField(help_text='Unique subscription identifier: 4 characters identifier, 2 characters checksum', unique=True, max_length=6, blank=True, default='------'),
        ),
        migrations.AddField(
            model_name='voucher',
            name='purpose',
            field=models.ForeignKey(related_name='vouchers', to='courses.VoucherPurpose'),
        ),

        migrations.RunPython(populate_status),

        migrations.RemoveField(
            model_name='subscribe',
            name='confirmed',
        ),
        migrations.RemoveField(
            model_name='subscribe',
            name='payed',
        ),
        migrations.RemoveField(
            model_name='subscribe',
            name='rejected',
        ),
    ]
