# Generated by Django 4.0.8 on 2023-01-06 19:43

from django.db import migrations, models
import django.db.models.deletion
import shortuuid.main
import utils.code_generator


def create_uuid(apps, schema_editor) -> None:
    for survey_instance in apps.get_model("survey", "surveyinstance").objects.all():
        survey_instance.url_key = shortuuid.uuid()
        survey_instance.save()


def copy_label_to_value(apps, schema_editor) -> None:
    translations = apps.get_model("survey", "choiceTranslation")
    for choice in apps.get_model("survey", "choice").objects.all():
        choice.value = (
            translations.objects.filter(master_id=choice.id).first().label[:32]
        )
        choice.save()


class Migration(migrations.Migration):
    replaces = [
        ("survey", "0002_surveyinstance_email_template"),
        ("survey", "0003_auto_20200326_1309"),
        ("survey", "0004_auto_20220325_2019"),
        ("survey", "0005_auto_20220325_2218"),
        ("survey", "0006_auto_20220327_0018"),
        ("survey", "0007_surveyinstance_is_completed"),
        ("survey", "0008_alter_surveyinstance_url_key"),
        ("survey", "0009_survey_teachers_allowed"),
    ]

    dependencies = [
        ("post_office", "0008_attachment_headers"),
        ("survey", "0001_squashed_0011_auto_20190904_1552"),
    ]

    operations = [
        migrations.AddField(
            model_name="surveyinstance",
            name="email_template",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="survey_instances",
                to="post_office.emailtemplate",
            ),
        ),
        migrations.AlterField(
            model_name="questiongroup",
            name="survey",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="survey.survey",
            ),
        ),
        migrations.AddField(
            model_name="questiongrouptranslation",
            name="title",
            field=models.CharField(
                blank=True, max_length=64, null=True, verbose_name="[TR] Title"
            ),
        ),
        migrations.AlterField(
            model_name="surveyinstance",
            name="last_update",
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.RenameModel(
            old_name="ScaleTemplateTranslation",
            new_name="ScaleTranslation",
        ),
        migrations.RenameField(
            model_name="answer",
            old_name="text",
            new_name="value",
        ),
        migrations.RemoveField(
            model_name="answer",
            name="choice",
        ),
        migrations.RenameField(
            model_name="question",
            old_name="scale_template",
            new_name="scale",
        ),
        migrations.AddField(
            model_name="surveytranslation",
            name="title",
            field=models.CharField(
                blank=True, max_length=64, null=True, verbose_name="[TR] Title"
            ),
        ),
        migrations.RenameModel(
            old_name="ScaleTemplate",
            new_name="Scale",
        ),
        migrations.AlterModelOptions(
            name="scaletranslation",
            options={
                "default_permissions": (),
                "managed": True,
                "verbose_name": "scale Translation",
            },
        ),
        migrations.RemoveField(
            model_name="scaletranslation",
            name="mid",
        ),
        migrations.AlterField(
            model_name="question",
            name="scale",
            field=models.ForeignKey(
                blank=True,
                help_text='Only needed for question type "choice"',
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="survey.scale",
            ),
        ),
        migrations.AlterModelTable(
            name="scaletranslation",
            table="survey_scale_translation",
        ),
        migrations.AddField(
            model_name="surveyinstance",
            name="url_key",
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.RunPython(
            code=create_uuid,
        ),
        migrations.AlterField(
            model_name="surveyinstance",
            name="url_key",
            field=models.CharField(
                default=utils.CodeGenerator.short_uuid(), max_length=32, unique=True
            ),
        ),
        migrations.AddField(
            model_name="choice",
            name="value",
            field=models.CharField(default="<none>", max_length=32),
            preserve_default=False,
        ),
        migrations.RunPython(
            code=copy_label_to_value,
        ),
        migrations.AlterModelOptions(
            name="questiongroup",
            options={"ordering": ["survey__name", "position"]},
        ),
        migrations.AlterField(
            model_name="question",
            name="scale",
            field=models.ForeignKey(
                blank=True,
                help_text='Only needed for question type "scale"',
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="survey.scale",
            ),
        ),
        migrations.AddField(
            model_name="surveyinstance",
            name="is_completed",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="surveyinstance",
            name="url_key",
            field=models.CharField(
                default=utils.code_generator.CodeGenerator.short_uuid,
                max_length=32,
                unique=True,
            ),
        ),
        migrations.AddField(
            model_name="survey",
            name="teachers_allowed",
            field=models.BooleanField(
                default=False,
                help_text="If set to true, teachers will be able to view the answers for their courses.",
            ),
        ),
    ]
