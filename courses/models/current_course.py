from courses import managers
from . import Course


class CurrentCourse(Course):
    objects = managers.CurrentCourseManager()

    class Meta:
        proxy = True
