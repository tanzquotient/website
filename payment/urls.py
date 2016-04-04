from django.conf.urls import patterns, url, include

from payment import views
from django.contrib.auth.decorators import login_required, permission_required

urlpatterns = patterns('',
                       url(r'^auth/counterpayment/(?P<usi>[a-zA-Z0-9]{6})/details/payed/$',
                           permission_required('counterpayment')(views.counterpayment_mark_payed),
                           name='counterpayment_pay'),
                       url(r'^auth/counterpayment/(?P<usi>[a-zA-Z0-9]{6})/details/$',
                           permission_required('counterpayment')(views.CounterPaymentDetailView.as_view()),
                           name='counterpayment_detail'),
                       url(r'^auth/counterpayment/$',
                           permission_required('counterpayment')(views.CounterPaymentIndexView.as_view()),
                           name='counterpayment_index'),
                       url(r'^payment/(?P<usi>[a-zA-Z0-9]{6})/payed/$', views.VoucherPaymentSuccessView.as_view(),
                           name='voucherpayment_success'),
                       url(r'^payment/(?P<usi>[a-zA-Z0-9]{6})/$', views.VoucherPaymentIndexView.as_view(),
                           name='voucherpayment_index'),
                       url(r'^auth/coursepayment/$',
                           permission_required('coursepayment')(views.CoursePaymentIndexView.as_view()),
                           name='coursepayment_index'),
                       # TODO Create counterpayment permission at the right place
                       )
