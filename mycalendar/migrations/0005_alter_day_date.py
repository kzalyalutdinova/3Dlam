# Generated by Django 5.0.6 on 2024-07-02 08:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mycalendar', '0004_alter_day_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='day',
            name='date',
            field=models.DateField(editable=False, unique=True, verbose_name='Date'),
        ),
    ]
