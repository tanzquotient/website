from courses import managers
from . import Course


class PlannedCourse(Course):
    objects = managers.PlannedCourseManager()

    class Meta:
        proxy = True
