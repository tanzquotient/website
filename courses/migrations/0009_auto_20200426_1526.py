# Generated by Django 2.2.12 on 2020-04-26 15:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0001_initial'),
        ('courses', '0008_userprofile_language'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='partner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='courses', to='partners.Partner'),
        ),
        migrations.AlterField(
            model_name='offering',
            name='type',
            field=models.CharField(choices=[('reg', 'Regular (weekly)'), ('irr', 'Irregular (e.g. workshops)'), ('p', 'Partner (external)')], default='reg', help_text='The type of the offering influences how the offering is displayed.', max_length=3),
        ),
    ]