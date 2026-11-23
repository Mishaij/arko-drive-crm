from django.test import TestCase
from django.urls import reverse

from .models import LessonBooking, Vehicle


class LessonBookingTests(TestCase):
    def setUp(self):
        self.vehicle = Vehicle.objects.create(name="Toyota Corolla")

    def valid_data(self):
        return {
            "first_name": "Անի",
            "last_name": "Սարգսյան",
            "phone": "+374 99 123 456",
            "lesson_date": "2026-12-10",
            "lesson_time": "14:30",
            "instructor": "Արամ",
            "car": str(self.vehicle.pk),
            "amount": "12000",
            "deposit": "4000",
        }

    def test_form_page_opens(self):
        response = self.client.get(reverse("main:booking_create"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Նոր գրանցում")
        self.assertContains(response, '<option value="14:30">14:30</option>', html=True)
        self.assertNotContains(response, ">AM<")
        self.assertNotContains(response, ">PM<")
        self.assertContains(response, "Toyota Corolla")
        self.assertNotContains(response, "Arko Drive")
        self.assertNotContains(response, "Գրանցում <br>")

    def test_download_button_creates_pdf_without_saving(self):
        data = self.valid_data()
        data["action"] = "download_pdf"
        response = self.client.post(reverse("main:booking_create"), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertTrue(response.content.startswith(b"%PDF"))
        self.assertEqual(LessonBooking.objects.count(), 0)

    def test_save_button_redirects_to_booking_list(self):
        data = self.valid_data()
        data["action"] = "save"
        response = self.client.post(reverse("main:booking_create"), data)
        self.assertRedirects(response, reverse("main:booking_list"))
        self.assertEqual(LessonBooking.objects.count(), 1)
        self.assertEqual(LessonBooking.objects.get().car, "Toyota Corolla")

    def test_only_active_admin_vehicles_are_available(self):
        Vehicle.objects.create(name="Inactive Car", is_active=False)
        response = self.client.get(reverse("main:booking_create"))
        self.assertContains(response, "Toyota Corolla")
        self.assertNotContains(response, "Inactive Car")

    def test_invalid_deposit_is_not_saved(self):
        data = self.valid_data()
        data["deposit"] = "13000"
        response = self.client.post(reverse("main:booking_create"), data)
        self.assertContains(response, "Կանխավճարը չի կարող գերազանցել գումարը")
        self.assertEqual(LessonBooking.objects.count(), 0)

    def create_booking(self, **overrides):
        data = {
            "first_name": "Անի",
            "last_name": "Սարգսյան",
            "phone": "+374 99 123 456",
            "lesson_date": "2026-12-10",
            "lesson_time": "14:30",
            "instructor": "Արամ",
            "car": "Toyota Corolla",
            "amount": 12000,
            "deposit": 4000,
        }
        data.update(overrides)
        return LessonBooking.objects.create(**data)

    def test_booking_list_displays_saved_records(self):
        booking = self.create_booking()
        response = self.client.get(reverse("main:booking_list"))
        self.assertContains(response, booking.first_name)
        self.assertContains(response, booking.last_name)
        self.assertContains(response, booking.phone)

    def test_search_works_by_first_name_last_name_and_phone(self):
        self.create_booking()
        self.create_booking(
            first_name="Դավիթ",
            last_name="Մանուկյան",
            phone="+374 77 987 654",
        )

        for query, expected, excluded in (
            ("Անի", "Սարգսյան", "Մանուկյան"),
            ("Մանուկ", "Դավիթ", "Անի"),
            ("987", "Դավիթ", "Անի"),
        ):
            with self.subTest(query=query):
                response = self.client.get(reverse("main:booking_list"), {"q": query})
                self.assertContains(response, expected)
                self.assertNotContains(response, excluded)

    def test_selected_day_pdf_contains_all_day_bookings(self):
        self.create_booking(first_name="Անի", lesson_date="2026-12-10", lesson_time="09:00")
        self.create_booking(first_name="Դավիթ", lesson_date="2026-12-10", lesson_time="14:30")
        self.create_booking(first_name="Այլ օր", lesson_date="2026-12-11")

        response = self.client.get(reverse("main:day_pdf"), {"date": "2026-12-10"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertTrue(response.content.startswith(b"%PDF"))

    def test_selected_day_without_bookings_returns_to_list(self):
        response = self.client.get(reverse("main:day_pdf"), {"date": "2026-12-31"})
        self.assertRedirects(
            response,
            reverse("main:booking_list") + "?date_from=2026-12-31&date_to=2026-12-31",
        )

    def test_date_range_filters_bookings(self):
        self.create_booking(
            first_name="Վաղ",
            lesson_date="2026-11-05",
        )
        self.create_booking(
            first_name="Միջին",
            lesson_date="2026-11-15",
        )
        self.create_booking(
            first_name="Ուշ",
            lesson_date="2026-11-25",
        )

        response = self.client.get(
            reverse("main:booking_list"),
            {"date_from": "2026-11-10", "date_to": "2026-11-20"},
        )
        self.assertContains(response, "Միջին")
        self.assertNotContains(response, "Վաղ")
        self.assertNotContains(response, "Ուշ")
