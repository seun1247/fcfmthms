from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):

    list_display = (
        'appointment_id',
        'student',
        'appointment_type',
        'doctor',
        'date',
        'time',
        'status',
    )

    list_filter = (
        'status',
        'appointment_type',
        'date',
    )

    search_fields = (
        'appointment_id',
        'student__full_name',
        'student__reg_number',
    )

    readonly_fields = (
        'appointment_id',
        'created_at',
    )

    fieldsets = (

        ('Appointment Information', {
            'fields': (
                'appointment_id',
                'student',
                'appointment_type',
                'doctor',
            )
        }),

        ('Schedule', {
            'fields': (
                'date',
                'time',
            )
        }),

        ('Status Control', {
            'fields': (
                'status',
                'admin_note',
                'cancellation_reason',
            )
        }),

        ('System Info', {
            'fields': (
                'created_at',
            )
        }),

    )