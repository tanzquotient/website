from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.views import View

from courses.models import Course


class TeacherPresenceEnabled(View):
    """
    Mixin to ensure only teachers of a specific course can access a course specific view.
    The specific view is defined by course parameter in kwargs!
    """

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        # check permissions not expressed by auth.perm
        allowed = False
        self.can_edit = False

        user = self.request.user
        course = Course.objects.get(id=int(kwargs["course"]))

        if (
            user.is_superuser
            or user.has_perm("courses.change_lesson_occurrence")
            or user.teaching_courses.filter(course=course).exists()
        ):
            allowed = True
            self.can_edit = True

        if user.is_staff or user.lesson_occurrences.filter(course=course).exists():
            allowed = True

        if not allowed:
            raise PermissionDenied

        return super(TeacherPresenceEnabled, self).dispatch(*args, **kwargs)
