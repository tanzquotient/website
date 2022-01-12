from django.urls import path, register_converter

from payment import views
from .converters import UsiPathConverter

register_converter(UsiPathConverter, 'usi')

app_name = 'payment'
urlpatterns = [
    path('auth/counterpayment/<usi:usi>/details/', views.CounterPaymentDetailView.as_view(), name='counterpayment_detail'),
    path('auth/counterpayment/', views.CounterPaymentIndexView.as_view(), name='counterpayment_index'),
    path('payment/<usi:usi>/paid/', views.VoucherPaymentSuccessView.as_view(), name='voucherpayment_success'),
    path('payment/<usi:usi>/', views.VoucherPaymentIndexView.as_view(), name='voucherpayment_index'),
    path('auth/coursepayment/', views.CoursePaymentIndexView.as_view(), name='coursepayment_index'),
    path('auth/coursepayment/<int:course>/', views.CoursePaymentDetailView.as_view(), name='coursepayment_detail'),
    path('auth/coursepayment/<int:course>/export/csv', views.CoursePaymentExportCsv.as_view(), name='coursepayment_export_csv'),
    path('auth/coursepayment/<int:course>/export/vcard', views.CoursePaymentExportVCard.as_view(), name='coursepayment_export_vcard'),
    path('auth/coursepayment/<int:course>/export/', views.CoursePaymentExportExcel.as_view(), name='coursepayment_export'),
    path('auth/coursepayment/<int:course>/<usi:usi>/', views.CoursePaymentConfirm.as_view(), name='coursepayment_confirm'),
    path('auth/coursepayment/<int:course>/<usi:usi>/paid/', views.CoursePaymentConfirm.as_view(), name='coursepayment_paid'),
    path('auth/finance/<int:offering>/detail/', views.OfferingFinanceDetailView.as_view(), name='offering_finance_detail_view'),
    path('auth/finance/<int:offering>/subscribers/', views.OfferingFinanceOverviewSubscribers.as_view(), name='offering_finance_overview_subscribers'),
    path('auth/finance/<int:offering>/teachers/', views.OfferingFinanceOverviewTeachers.as_view(), name='offering_finance_overview_teachers'),
    path('auth/finance/', views.OfferingFinanceIndexView.as_view(), name='offering_finance_index_view'),
    path('auth/finance/account/index/', views.AccountFinanceIndexView.as_view(), name='account_finance_index_view'),
    path('auth/finance/account/detail/', views.AccountFinanceDetailView.as_view(), name='account_finance_detail_view'),
]
