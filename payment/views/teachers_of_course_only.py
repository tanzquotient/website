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
        course_id = kwargs['course']

        if user.is_superuser or user.has_perm('courses.change_subscribe'):
            allowed = True
        if user.teaching_courses.filter(course__id=course_id).exists():
            allowed = True

        if not allowed:
            raise PermissionDenied

        return super(TeacherOfCourseOnly, self).dispatch(*args, **kwargs)