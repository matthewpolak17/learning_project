# Generated by Django 4.2.5 on 2023-10-26 01:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="attempt",
            name="number",
            field=models.IntegerField(default=0),
        ),
    ]
