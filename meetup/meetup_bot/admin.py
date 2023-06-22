from django.contrib import admin

from .models import *


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = (
        'telegram',
        'role',
    )


admin.site.register(Presentation)
admin.site.register(Form)
