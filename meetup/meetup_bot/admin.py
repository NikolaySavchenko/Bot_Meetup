from django.contrib import admin

from .models import *


@admin.register(Presentation)
class PresentationAdmin(admin.ModelAdmin):
    list_display = (
        'member',
        'topic',
    )


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = (
        'telegram',
        'role',
    )


@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = (
        'member',
        'name',
        'job',
        'region'
    )
