from django.contrib import admin

from .models import *


@admin.register(Presentation)
class PresentationAdmin(admin.ModelAdmin):
    list_display = (
        'start_time',
        'member',
        'topic',
        'duration'
    )


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = (
        'telegram_name',
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


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = (
        'member',
        'donation'
    )
