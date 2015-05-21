from django.contrib import admin

from models import *

# Register your models here.

class ProblemAdmin(admin.ModelAdmin):
    list_display = ('datetime', 'tag', 'priority', 'message',)


admin.site.register(Problem, ProblemAdmin)
