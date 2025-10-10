from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.views import View


class TeacherOfCourseOnly(View):
    """
    Mixin to ensure only teachers of a specific course can access a course specific view.
    The specific view is defined by course parameter in kwargs!
    """

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        # check permissions not expressed by auth.perm
        allowed = False

        user = self.request.user

        if user.is_superuser or user.has_perm("courses.change_subscribe"):
            allowed = True

        if (
            "course" in kwargs
            and user.teaching_courses.filter(course__id=kwargs["course"]).exists()
        ):
            allowed = True

        if (
            "lesson" in kwargs
            and user.teaching_courses.filter(
                course__lesson_occurrences__id=kwargs["lesson"]
            ).exists()
        ):
            allowed = True

        if not allowed:
            raise PermissionDenied

        return super(TeacherOfCourseOnly, self).dispatch(*args, **kwargs)
