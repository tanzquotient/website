from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.views import View


class TeacherOnly(View):
    """
    Mixin to ensure only teachers can access a view.
    """

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        # check permissions not expressed by auth.perm
        if (
            not self.request.user.is_staff
            and not self.request.user.profile.is_teacher()
            and not self.request.user.has_perm("courses.change_subscribe")
        ):
            raise PermissionDenied

        return super(TeacherOnly, self).dispatch(*args, **kwargs)
