from django.contrib import admin
from .models import UpFile

class UpFileAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields':['path', 'status', 'user']}), 
        ('Upload date infomation', {'fields':['up_date'], 'classes':['collapse']}),
    ]
admin.site.register(UpFile)
