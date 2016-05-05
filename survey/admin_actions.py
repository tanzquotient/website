#!/usr/bin/python
# -*- coding: UTF-8 -*-

import services

def send_invitations(modeladmin, request, queryset):
    for survey_inst in queryset:
        services.send_invitation(survey_inst)


send_invitations.short_description = "Send invitations to those which did not already get one."


def export_surveys_xlsx(modeladmin, request, queryset):
    return services.export_surveys(queryset.all())


export_surveys_xlsx.short_description = "Export selected surveys as several XLSX-files"

