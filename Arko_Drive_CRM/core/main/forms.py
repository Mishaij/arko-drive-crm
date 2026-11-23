import re

from django import forms
from django.core.exceptions import ValidationError

from .models import LessonBooking, Vehicle

TIME_CHOICES = [
    (f"{hour:02d}:{minute:02d}", f"{hour:02d}:{minute:02d}")
    for hour in range(24)
    for minute in (0, 15, 30, 45)
]

class LessonBookingForm(forms.ModelForm):
    car = forms.ModelChoiceField(
        label="Մեքենա",
        queryset=Vehicle.objects.filter(is_active=True).order_by("sort_order", "name"),
        empty_label="Ընտրեք մեքենան",
    )

    class Meta:
        model = LessonBooking
        fields = (
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
        widgets = {
            "first_name": forms.TextInput(
                attrs={"placeholder": "Օր․ Անի", "autocomplete": "given-name"}
            ),
            "last_name": forms.TextInput(
                attrs={"placeholder": "Օր․ Սարգսյան", "autocomplete": "family-name"}
            ),
            "phone": forms.TextInput(
                attrs={
                    "placeholder": "+374 00 000 000",
                    "autocomplete": "tel",
                    "inputmode": "tel",
                }
            ),
            "lesson_date": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
            "lesson_time": forms.Select(choices=TIME_CHOICES),
            "instructor": forms.TextInput(attrs={"placeholder": "Անուն, ազգանուն"}),
            "amount": forms.NumberInput(attrs={"placeholder": "0", "min": 0, "step": 1}),
            "deposit": forms.NumberInput(attrs={"placeholder": "0", "min": 0, "step": 1}),
        }

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        digits = re.sub(r"\D", "", phone)
        if not re.fullmatch(r"\+?[\d\s().-]+", phone) or not 7 <= len(digits) <= 15:
            raise ValidationError("Մուտքագրեք վավեր հեռախոսահամար։")
        return phone

    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get("amount")
        deposit = cleaned_data.get("deposit")
        if amount is not None and deposit is not None and deposit > amount:
            self.add_error("deposit", "Կանխավճարը չի կարող գերազանցել գումարը։")
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        vehicle = self.cleaned_data.get("car")
        if vehicle:
            instance.car = vehicle.name
        if commit:
            instance.save()
        return instance
