# Generated by Django 4.1 on 2023-11-18 05:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0014_semester_is_current'),
    ]

    operations = [
        migrations.AlterField(
            model_name='semester',
            name='is_current',
            field=models.BooleanField(default=True),
        ),
    ]
