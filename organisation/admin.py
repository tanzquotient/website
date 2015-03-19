from django.contrib import admin
from organisation.models import Function

# Register your models here.
class FunctionAdmin(admin.ModelAdmin):
    list_display=('name','email','active','user',)
    
# Register your models here.
admin.site.register(Function, FunctionAdmin)