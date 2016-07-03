from rest_framework import permissions


class TeacherCanReadUpdateSubscriptionPermission(permissions.IsAuthenticated):
    """Allow only teachers to read and update existing instances (no creation/deletion is allowed)"""

    def has_object_permission(self, request, view, obj=None):
        if not super(TeacherCanReadUpdateSubscriptionPermission, self).has_object_permission(request, view, obj):
            return False
        if obj is None:
            # Either a list or a create, so no author
            can_edit = False
        else:
            can_edit = obj.course.teachers.filter(id=request.user.id).count() != 0
        return can_edit


class TeacherCanReadUpdateCoursePermission(permissions.IsAuthenticated):
    """Allow only teachers to read and update existing instances (no creation/deletion is allowed)"""

    def has_object_permission(self, request, view, obj=None):
        print("check")
        if not super(TeacherCanReadUpdateCoursePermission, self).has_object_permission(request, view, obj):
            return False
        if obj is None:
            # Either a list or a create, so no author
            can_edit = False
        else:
            can_edit = obj.teachers.filter(id=request.user.id).count() != 0
        return can_edit
