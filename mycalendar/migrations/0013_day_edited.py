# Generated by Django 5.0.6 on 2024-07-12 08:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mycalendar', '0012_monthyear_days_amount_monthyear_month_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='day',
            name='edited',
            field=models.BooleanField(default=False, verbose_name='Day has been edited'),
        ),
    ]
