from django.conf.urls import url, include

from courses import views
from courses import admin_views
import courses.api.urls

app_name = 'courses'
urlpatterns = [
    url(r'^$', views.course_list, name='home'),
    url(r'^list/$', views.course_list, name='list'),
    url(r'^list/(?P<subscription_type>\w+)/(?P<style_name>\w+)/$', views.course_list, name='list_style'),
    url(r'^preview/$', views.course_list_preview, name='list_preview'),
    url(r'^archive/$', views.archive, name='archive'),
    url(r'^(?P<course_id>\d+)/detail/$', views.course_detail, name='course_detail'),
    url(r'^(?P<course_id>\d+)/subscribe_form/$', views.subscribe_form, name='subscribe_form'),
    url(r'^(?P<course_id>\d+)/subscribe/$', views.subscribe, name='subscribe'),
    url(r'^offering/(?P<offering_id>\d+)/$', views.offering_by_id, name='offering_by_id'),
    url(r'^auth/$', views.subscription_overview,
        name='subscription_overview'),
    url(r'^auth/export/excel$', views.export_summary_excel, name='export_summary_excel'),
    url(r'^auth/export/$', views.export_summary, name='export_summary'),
    url(r'^auth/export/(?P<offering_id>\d+)/excel$', views.export_offering_summary_excel, name='export_offering_summary_excel'),
    url(r'^auth/export/(?P<offering_id>\d+)/$', views.export_offering_summary, name='export_offering_summary'),
    url(r'^auth/export/teacher/(?P<offering_id>\d+)/excel$', views.export_offering_teacher_payment_information_excel, name='export_offering_salary_excel'),
    url(r'^auth/export/teacher/(?P<offering_id>\d+)/$', views.export_offering_teacher_payment_information, name='export_offering_salary'),
    url(r'^auth/courses/(?P<course_id>\d+)/$', views.course_overview,
        name='course_overview'),
    url(r'^auth/offering/(?P<offering_id>\d+)/$', views.offering_overview,
        name='offering_overview'),
    url(r'^admin/voucher_generate/$', admin_views.voucher_generation_view,
        name='voucher_generation'),
    url(r'^api/', include(courses.api.urls, namespace='courses_api')),  # nested namespace 'api'
]
