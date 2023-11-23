from payment.views import TeacherOfCourseOnly


class CoursePaymentExportVCard(TeacherOfCourseOnly):
    def get(self, request, *args, **kwargs):
        from courses import services

        return services.export_subscriptions([kwargs.get("course", None)], "vcard")
