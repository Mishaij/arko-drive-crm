from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="LessonBooking",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("first_name", models.CharField(max_length=60, verbose_name="Անուն")),
                ("last_name", models.CharField(max_length=60, verbose_name="Ազգանուն")),
                ("phone", models.CharField(max_length=30, verbose_name="Հեռախոսահամար")),
                ("lesson_date", models.DateField(verbose_name="Ամիս, ամսաթիվ")),
                ("lesson_time", models.TimeField(verbose_name="Ժամ")),
                ("instructor", models.CharField(blank=True, max_length=80, verbose_name="Հրահանգիչ")),
                ("car", models.CharField(max_length=100, verbose_name="Մեքենա")),
                ("amount", models.DecimalField(decimal_places=0, max_digits=12, verbose_name="Գումար")),
                ("deposit", models.DecimalField(blank=True, decimal_places=0, max_digits=12, null=True, verbose_name="Կանխավճար")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Ստեղծվել է")),
            ],
            options={
                "verbose_name": "Վարորդական դասի գրանցում",
                "verbose_name_plural": "Վարորդական դասի գրանցումներ",
                "ordering": ["-lesson_date", "-lesson_time"],
            },
        )
    ]
