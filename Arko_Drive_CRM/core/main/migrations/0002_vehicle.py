from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("main", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="Vehicle",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, unique=True, verbose_name="Մեքենայի անվանում")),
                ("is_active", models.BooleanField(default=True, verbose_name="Ակտիվ")),
                ("sort_order", models.PositiveIntegerField(default=0, verbose_name="Հերթականություն")),
            ],
            options={
                "verbose_name": "Մեքենա",
                "verbose_name_plural": "Մեքենաներ",
                "ordering": ["sort_order", "name"],
            },
        )
    ]
