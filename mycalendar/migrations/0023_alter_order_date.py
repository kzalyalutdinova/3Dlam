# Generated by Django 5.0.6 on 2024-09-04 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mycalendar', '0022_printer_order_printingregister'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='date',
            field=models.CharField(max_length=30, verbose_name='Month and year of the order'),
        ),
    ]
