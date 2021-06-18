from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0009_auto_20200426_1526'),
    ]

    operations = [
        migrations.RunSQL(
            sql='CREATE VIEW courses_with_period AS '
                'SELECT course.*, period.date_from, period.date_to '
                'FROM courses_course course '
                'LEFT JOIN courses_offering offering ON course.offering_id = offering.id '
                'LEFT JOIN courses_period period ON '
                '   (course.period_id IS NOT NULL AND period.id = course.period_id) '
                '   OR (course.period_id IS NULL AND course.offering_id IS NOT NULL AND offering.period_id = period.id)'
        ),
        migrations.RunSQL(
            sql='CREATE VIEW past_courses AS '
                'SELECT * FROM courses_with_period WHERE date_to < now()'
        ),
        migrations.RunSQL(
            sql='CREATE VIEW current_courses AS '
                'SELECT * FROM courses_with_period '
                'WHERE date_from <= now() AND date_to >= now()'
        ),
        migrations.RunSQL(
            sql='CREATE VIEW current_user_courses AS '
                'SELECT courses.*, subscription.user_id '
                'FROM current_courses as courses '
                'JOIN courses_subscribe subscription on subscription.course_id = courses.id'
        ),
        migrations.RunSQL(
            sql='CREATE VIEW past_courses_users AS '
                'SELECT courses.*, subscription.user_id '
                'FROM past_courses as courses '
                'JOIN courses_subscribe subscription on subscription.course_id = courses.id'
        ),
    ]
