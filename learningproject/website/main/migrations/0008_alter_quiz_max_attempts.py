# Generated by Django 4.2.5 on 2023-11-14 21:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0007_alter_quiz_max_attempts"),
    ]

    operations = [
        migrations.AlterField(
            model_name="quiz",
            name="max_attempts",
            field=models.IntegerField(default=3),
        ),
    ]