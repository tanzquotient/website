from courses.models import Course


def role(user_id: int, course: Course) -> str:
    for subscribe in course.subscriptions.all():
        if subscribe.user_id == user_id:
            return subscribe.assigned_role()
    raise ValueError("User is not subscribed to course")
