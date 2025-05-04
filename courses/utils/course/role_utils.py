from courses.models import LessonOccurrence


def role(user_id: int, lesson: LessonOccurrence) -> str:
    for subscribe in lesson.course.subscriptions.all():
        if subscribe.user_id == user_id:
            return subscribe.assigned_role()
    for attendance in lesson.attendances.all():
        if attendance.user_id == user_id:
            return attendance.role
    raise ValueError("User is not subscribed to course")
