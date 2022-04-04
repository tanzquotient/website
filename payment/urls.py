from django.urls import path, register_converter

from .converters import UsiPathConverter
from .views import *

register_converter(UsiPathConverter, 'usi')

app_name = 'payment'
urlpatterns = [
    path('auth/counterpayment/<usi:usi>/details/', CounterPaymentDetailView.as_view(), name='counterpayment_detail'),
    path('auth/counterpayment/', CounterPaymentIndexView.as_view(), name='counterpayment_index'),
    path('payment/<usi:usi>/', subscription_payment_view, name='subscription_payment'),
    path('auth/courses/', CoursesAsTeacherList.as_view(), name='courses_as_teacher_list'),
    path('auth/courses/<int:course>/', CoursePaymentDetailView.as_view(), name='coursepayment_detail'),
    path('auth/courses/<int:course>/export/csv', CoursePaymentExportCsv.as_view(), name='coursepayment_export_csv'),
    path('auth/courses/<int:course>/export/vcard', CoursePaymentExportVCard.as_view(), name='coursepayment_export_vcard'),
    path('auth/courses/<int:course>/export/', CoursePaymentExportExcel.as_view(), name='coursepayment_export'),
    path('auth/courses/<int:course>/<usi:usi>/', CoursePaymentConfirm.as_view(), name='coursepayment_confirm'),
    path('auth/courses/<int:course>/<usi:usi>/paid/', CoursePaymentConfirm.as_view(), name='coursepayment_paid'),
    path('auth/finance/<int:offering>/detail/', OfferingFinanceDetailView.as_view(), name='offering_finance_detail_view'),
    path('auth/finance/<int:offering>/subscribers/', OfferingFinanceOverviewSubscribers.as_view(), name='offering_finance_overview_subscribers'),
    path('auth/finance/<int:offering>/teachers/', OfferingFinanceOverviewTeachers.as_view(), name='offering_finance_overview_teachers'),
    path('auth/finance/', OfferingFinanceIndexView.as_view(), name='offering_finance_index_view'),
    path('auth/finance/account/index/', AccountFinanceIndexView.as_view(), name='account_finance_index_view'),
    path('auth/finance/account/detail/', AccountFinanceDetailView.as_view(), name='account_finance_detail_view'),
]
