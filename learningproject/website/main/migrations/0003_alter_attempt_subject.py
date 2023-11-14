# Generated by Django 4.2.5 on 2023-11-01 15:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0002_attempt_number"),
    ]

    operations = [
        migrations.AlterField(
            model_name="attempt",
            name="subject",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="attempts",
                to="main.subject",
            ),
        ),
    ]