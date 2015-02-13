from django.contrib import admin
from models import *

# Register your models here.

class ProblemAdmin(admin.ModelAdmin):
    list_display = ('datetime', 'tag', 'priority', 'message', )
    
    # define the related_lookup_fields
    related_lookup_fields = {
        'generic': [['content_type', 'object_id'],],
    }

admin.site.register(Problem, ProblemAdmin)