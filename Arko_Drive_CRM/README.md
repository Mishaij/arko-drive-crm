# Arko Drive CRM

Internal CRM and lesson-booking system for a driving school. The application provides an Armenian-language interface for creating, searching, filtering, and exporting driving lesson bookings.

## Features

- Create driving lesson bookings with student, contact, schedule, instructor, vehicle, price, and deposit details.
- Validate phone numbers and prevent deposits from exceeding the total lesson price.
- Manage vehicles through Django Admin, including active/inactive status and display order.
- Show only active vehicles in the booking form.
- Search bookings by first name, last name, or phone number.
- Filter bookings by a date range.
- Export an individual booking as a PDF.
- Export all bookings for a selected day as a structured PDF schedule.
- Render Armenian text in generated PDFs using an embedded TrueType font.
- Use 24-hour time selection with 15-minute intervals.
- Include automated tests for forms, filtering, PDF generation, and vehicle availability.

## Tech stack

- Python
- Django 5.2+
- SQLite
- ReportLab
- HTML, CSS

## Project structure

```text
Arko_Drive_CRM/
├── core/
│   ├── core/       # Django project configuration
│   ├── main/       # Booking application
│   ├── manage.py
│   ├── requirements.txt
│   └── db.sqlite3  # Local database, excluded from Git
└── README.md
```

## Installation

### Windows PowerShell

```powershell
cd core
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### macOS / Linux

```bash
cd core
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open the application at <http://127.0.0.1:8000/>.

- Booking interface: `/`
- Booking list: `/bookings/`
- Admin panel: `/admin/`

## Running tests

```bash
cd core
python manage.py test
```

## Resume description

**Arko Drive CRM — Django Web Application**

Developed an Armenian-language CRM and lesson-booking system for a driving school using Django, SQLite, HTML/CSS, and ReportLab. Implemented booking management, Django Admin vehicle configuration, form validation, search and date-range filtering, and PDF exports for individual bookings and daily schedules. Added automated tests covering core workflows, validation, filtering, and PDF generation.

## Notes

This project is configured for local development. Before deploying it to production, configure environment variables, disable `DEBUG`, set a secure `SECRET_KEY`, configure allowed hosts, use a production database, and serve static files through a production web server.
