# Generated by Django 4.1 on 2023-11-18 04:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_alter_semester_num'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='semester',
            name='num',
        ),
        migrations.AddField(
            model_name='semester',
            name='name',
            field=models.CharField(default='def', max_length=255),
        ),
    ]