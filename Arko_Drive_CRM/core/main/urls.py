from django.urls import path

from .views import booking_create, booking_list, day_pdf

app_name = "main"

urlpatterns = [
    path("", booking_create, name="booking_create"),
    path("bookings/", booking_list, name="booking_list"),
    path("bookings/day-pdf/", day_pdf, name="day_pdf"),
]
