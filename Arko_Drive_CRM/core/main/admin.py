from django.contrib import admin

from .models import LessonBooking, Vehicle


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "sort_order")
    list_editable = ("is_active", "sort_order")
    search_fields = ("name",)
    ordering = ("sort_order", "name")


@admin.register(LessonBooking)
class LessonBookingAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "phone",
        "lesson_date",
        "lesson_time",
        "instructor",
        "car",
        "amount",
        "deposit",
    )
    list_filter = ("lesson_date", "instructor", "car")
    search_fields = ("first_name", "last_name", "phone", "instructor", "car")
    date_hierarchy = "lesson_date"
