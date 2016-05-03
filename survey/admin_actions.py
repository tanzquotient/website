#!/usr/bin/python
# -*- coding: UTF-8 -*-

import services

def send_invitations(modeladmin, request, queryset):
    for survey_inst in queryset:
        services.send_invitation(survey_inst)


send_invitations.short_description = "Send invitations to those which did not already get one."
