from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0010_added_sql_views'),
    ]

    operations = [
        migrations.RunSQL(
            sql='CREATE OR REPLACE VIEW current_courses AS '
                'SELECT * FROM courses_with_period '
                'WHERE date_to >= now()'
        ),
    ]
