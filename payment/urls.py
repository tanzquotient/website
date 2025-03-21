from django.urls import path, register_converter

from .converters import UsiPathConverter
from .views import *

register_converter(UsiPathConverter, "usi")

app_name = "payment"
urlpatterns = [
    path(
        "auth/counterpayment/<usi:usi>/details/",
        CounterPaymentDetailView.as_view(),
        name="counterpayment_detail",
    ),
    path(
        "auth/counterpayment/",
        CounterPaymentIndexView.as_view(),
        name="counterpayment_index",
    ),
    path("payment/<usi:usi>/", subscription_payment_view, name="subscription_payment"),
    path(
        "payment/<usi:usi>/qr-bill/",
        subscription_qr_bill_export_pdf,
        name="subscription_qr_bill_export_pdf",
    ),
    path(
        "auth/courses/", CoursesAsTeacherList.as_view(), name="courses_as_teacher_list"
    ),
    path(
        "auth/courses/<int:course>/",
        CoursePaymentDetailView.as_view(),
        name="coursepayment_detail",
    ),
    path(
        "auth/courses/<int:course>/teacher-presence",
        CourseTeacherPresenceView.as_view(),
        name="course_teacher_presence",
    ),
    path(
        "auth/courses/<int:course>/participants",
        CourseParticipantsView.as_view(),
        name="course_participants",
    ),
    path(
        "auth/teacher-search",
        search_teacher,
        name="teacher_search",
    ),
    path(
        "auth/courses/<int:course>/export/csv",
        CoursePaymentExportCsv.as_view(),
        name="coursepayment_export_csv",
    ),
    path(
        "auth/courses/<int:course>/export/vcard",
        CoursePaymentExportVCard.as_view(),
        name="coursepayment_export_vcard",
    ),
    path(
        "auth/courses/<int:course>/export/",
        CoursePaymentExportExcel.as_view(),
        name="coursepayment_export",
    ),
    path(
        "auth/courses/<int:course>/<usi:usi>/",
        CoursePaymentConfirm.as_view(),
        name="coursepayment_confirm",
    ),
    path(
        "auth/courses/<int:course>/<usi:usi>/paid/",
        CoursePaymentConfirm.as_view(),
        name="coursepayment_paid",
    ),
    # Finances for offerings
    path(
        "finance/",
        OfferingFinanceIndexView.as_view(),
        name="offering_finance_index_view",
    ),
    path(
        "finance/<int:offering>/unpaid/",
        OfferingFinanceUnpaidView.as_view(),
        name="offering_unpaid",
    ),
    path(
        "finance/<int:offering>/courses/",
        OfferingFinanceCourses.as_view(),
        name="offering_courses",
    ),
    path(
        "finance/<int:offering>/teachers/",
        OfferingFinanceTeachers.as_view(),
        name="offering_teachers",
    ),
    path(
        "finance/<int:offering_id>/revenue/",
        offering_finance_revenue,
        name="offering_revenue",
    ),
    path(
        "finance/<int:offering>/teachers/export/",
        offering_finance_teachers_export,
        name="offering_teachers_export",
    ),
    # List of transactions
    path(
        "auth/finance/account/index/",
        AccountFinanceIndexView.as_view(),
        name="account_finance_index_view",
    ),
    path(
        "auth/finance/account/detail/",
        AccountFinanceDetailView.as_view(),
        name="account_finance_detail_view",
    ),
]
