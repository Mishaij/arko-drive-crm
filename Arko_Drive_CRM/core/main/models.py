from django.db import models


class Vehicle(models.Model):
    name = models.CharField("Մեքենայի անվանում", max_length=100, unique=True)
    is_active = models.BooleanField("Ակտիվ", default=True)
    sort_order = models.PositiveIntegerField("Հերթականություն", default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "Մեքենա"
        verbose_name_plural = "Մեքենաներ"

    def __str__(self):
        return self.name


class LessonBooking(models.Model):
    first_name = models.CharField("Անուն", max_length=60)
    last_name = models.CharField("Ազգանուն", max_length=60)
    phone = models.CharField("Հեռախոսահամար", max_length=30)
    lesson_date = models.DateField("Ամիս, ամսաթիվ")
    lesson_time = models.TimeField("Ժամ")
    instructor = models.CharField("Հրահանգիչ", max_length=80, blank=True)
    car = models.CharField("Մեքենա", max_length=100)
    amount = models.DecimalField("Գումար", max_digits=12, decimal_places=0)
    deposit = models.DecimalField(
        "Կանխավճար",
        max_digits=12,
        decimal_places=0,
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField("Ստեղծվել է", auto_now_add=True)

    class Meta:
        ordering = ["-lesson_date", "-lesson_time"]
        verbose_name = "Վարորդական դասի գրանցում"
        verbose_name_plural = "Վարորդական դասի գրանցումներ"

    def __str__(self):
        return f"{self.first_name} {self.last_name} — {self.lesson_date} {self.lesson_time:%H:%M}"
