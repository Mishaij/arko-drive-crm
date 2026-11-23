from io import BytesIO
from pathlib import Path
from urllib.parse import quote
from datetime import date

from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q
from django.shortcuts import redirect, render
from django.urls import reverse
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from .forms import LessonBookingForm
from .models import LessonBooking

FONT_NAME = "ArkoDriveArmenian"
FONT_PATH = Path(__file__).parent / "static" / "main" / "fonts" / "DejaVuSans.ttf"
MONTHS = (
    "հունվարի",
    "փետրվարի",
    "մարտի",
    "ապրիլի",
    "մայիսի",
    "հունիսի",
    "հուլիսի",
    "օգոստոսի",
    "սեպտեմբերի",
    "հոկտեմբերի",
    "նոյեմբերի",
    "դեկտեմբերի",
)


def format_date(value):
    return f"{value.day} {MONTHS[value.month - 1]} {value.year} թ."


def format_money(value):
    if value is None:
        return "—"
    return f"{int(value):,} ֏".replace(",", " ")


def draw_fitted_text(pdf, text, x, y, max_width, font_size=15):
    text = str(text)
    current_size = font_size
    while current_size > 9 and pdfmetrics.stringWidth(text, FONT_NAME, current_size) > max_width:
        current_size -= 1

    if pdfmetrics.stringWidth(text, FONT_NAME, current_size) <= max_width:
        pdf.setFont(FONT_NAME, current_size)
        pdf.drawString(x, y, text)
        return

    shortened = text
    while shortened and pdfmetrics.stringWidth(shortened + "…", FONT_NAME, current_size) > max_width:
        shortened = shortened[:-1]
    pdf.setFont(FONT_NAME, current_size)
    pdf.drawString(x, y, shortened + "…")


def create_booking_pdf(booking):
    if FONT_NAME not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_PATH))

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4, pageCompression=1)
    width, height = A4

    pdf.setFillColor(HexColor("#142e25"))
    pdf.rect(0, height - 150, width, 150, stroke=0, fill=1)
    pdf.setFillColor(HexColor("#c6f36c"))
    pdf.rect(46, height - 48, 30, 4, stroke=0, fill=1)
    pdf.setFillColor(HexColor("#ffffff"))
    pdf.setFont(FONT_NAME, 23)
    pdf.drawString(46, height - 92, "Վարորդական դասի գրանցում")
    pdf.setFillColor(HexColor("#c9ded3"))
    pdf.setFont(FONT_NAME, 12)
    pdf.drawString(
        46,
        height - 119,
        f"{format_date(booking.lesson_date)}  ·  {booking.lesson_time:%H:%M}",
    )

    rows = (
        ("Անուն", booking.first_name),
        ("Ազգանուն", booking.last_name),
        ("Հեռախոսահամար", booking.phone),
        ("Ամիս, ամսաթիվ", format_date(booking.lesson_date)),
        ("Ժամ", booking.lesson_time.strftime("%H:%M")),
        ("Հրահանգիչ", booking.instructor or "—"),
        ("Մեքենա", booking.car),
        ("Գումար", format_money(booking.amount)),
        ("Կանխավճար", format_money(booking.deposit)),
    )

    y = height - 190
    for label, value in rows:
        pdf.setFillColor(HexColor("#34564a"))
        pdf.setFont(FONT_NAME, 10)
        pdf.drawString(46, y, label)
        pdf.setFillColor(HexColor("#182921"))
        draw_fitted_text(pdf, value, 46, y - 24, width - 92)
        pdf.setStrokeColor(HexColor("#dce7df"))
        pdf.line(46, y - 38, width - 46, y - 38)
        y -= 65

    pdf.showPage()
    pdf.save()
    return buffer.getvalue()


def booking_pdf_response(booking):
    pdf_data = create_booking_pdf(booking)
    filename = f"վարորդական-դաս-{booking.lesson_date.isoformat()}.pdf"
    response = HttpResponse(pdf_data, content_type="application/pdf")
    response["Content-Disposition"] = (
        "attachment; filename=driving-lesson.pdf; "
        f"filename*=UTF-8''{quote(filename)}"
    )
    return response


def booking_create(request):
    form = LessonBookingForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if request.POST.get("action") == "save":
            booking = form.save()
            messages.success(
                request,
                f"{booking.first_name} {booking.last_name} — գրանցումը պահպանված է։",
            )
            return redirect("main:booking_list")
        booking = form.save(commit=False)
        return booking_pdf_response(booking)

    return render(
        request,
        "main/booking_form.html",
        {"form": form},
    )


def booking_list(request):
    query = request.GET.get("q", "").strip()
    date_from_value = request.GET.get("date_from", "").strip()
    date_to_value = request.GET.get("date_to", "").strip()
    bookings = LessonBooking.objects.all()
    if query:
        bookings = bookings.filter(
            Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(phone__icontains=query)
        )

    try:
        date_from = date.fromisoformat(date_from_value) if date_from_value else None
    except ValueError:
        date_from = None
        date_from_value = ""

    try:
        date_to = date.fromisoformat(date_to_value) if date_to_value else None
    except ValueError:
        date_to = None
        date_to_value = ""

    if date_from:
        bookings = bookings.filter(lesson_date__gte=date_from)
    if date_to:
        bookings = bookings.filter(lesson_date__lte=date_to)

    return render(
        request,
        "main/booking_list.html",
        {
            "bookings": bookings,
            "query": query,
            "date_from": date_from_value,
            "date_to": date_to_value,
        },
    )


def create_day_pdf(bookings, selected_date):
    if FONT_NAME not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_PATH))

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4, pageCompression=1)
    width, height = A4
    bookings = list(bookings)

    def draw_header(page_number):
        pdf.setFillColor(HexColor("#142e25"))
        pdf.rect(0, height - 112, width, 112, stroke=0, fill=1)
        pdf.setFillColor(HexColor("#c6f36c"))
        pdf.rect(38, height - 36, 28, 4, stroke=0, fill=1)
        pdf.setFillColor(HexColor("#ffffff"))
        pdf.setFont(FONT_NAME, 20)
        pdf.drawString(38, height - 70, "Օրվա վարորդական դասերի գրանցումներ")
        pdf.setFillColor(HexColor("#c9ded3"))
        pdf.setFont(FONT_NAME, 10)
        pdf.drawString(
            38,
            height - 91,
            f"{format_date(selected_date)}  ·  {len(bookings)} գրանցում  ·  էջ {page_number}",
        )

    page_number = 1
    draw_header(page_number)
    y = height - 145

    for index, booking in enumerate(bookings, start=1):
        if y < 95:
            pdf.showPage()
            page_number += 1
            draw_header(page_number)
            y = height - 145

        pdf.setFillColor(HexColor("#155b44"))
        pdf.setFont(FONT_NAME, 9)
        pdf.drawString(38, y, f"{index}. {booking.lesson_time:%H:%M}")
        pdf.setFillColor(HexColor("#182921"))
        draw_fitted_text(
            pdf,
            f"{booking.first_name} {booking.last_name}",
            106,
            y,
            220,
            font_size=12,
        )
        draw_fitted_text(pdf, booking.phone, 345, y, 112, font_size=10)
        draw_fitted_text(pdf, booking.car, 470, y, 88, font_size=9)

        details = (
            f"Հրահանգիչ՝ {booking.instructor or '—'}   ·   "
            f"Գումար՝ {format_money(booking.amount)}   ·   "
            f"Կանխավճար՝ {format_money(booking.deposit)}"
        )
        pdf.setFillColor(HexColor("#60736a"))
        draw_fitted_text(pdf, details, 106, y - 20, width - 144, font_size=9)
        pdf.setStrokeColor(HexColor("#dce7df"))
        pdf.line(38, y - 33, width - 38, y - 33)
        y -= 53

    pdf.showPage()
    pdf.save()
    return buffer.getvalue()


def day_pdf(request):
    date_value = request.GET.get("date", "").strip()
    try:
        selected_date = date.fromisoformat(date_value)
    except ValueError:
        messages.error(request, "Ընտրեք ճիշտ ամսաթիվ։")
        return redirect("main:booking_list")

    bookings = LessonBooking.objects.filter(lesson_date=selected_date).order_by("lesson_time")
    if not bookings.exists():
        messages.warning(request, "Ընտրված օրվա համար գրանցումներ չկան։")
        list_url = reverse("main:booking_list")
        return redirect(f"{list_url}?date_from={date_value}&date_to={date_value}")

    pdf_data = create_day_pdf(bookings, selected_date)
    filename = f"օրվա-գրանցումներ-{selected_date.isoformat()}.pdf"
    response = HttpResponse(pdf_data, content_type="application/pdf")
    response["Content-Disposition"] = (
        f"attachment; filename=bookings-{selected_date.isoformat()}.pdf; "
        f"filename*=UTF-8''{quote(filename)}"
    )
    return response
