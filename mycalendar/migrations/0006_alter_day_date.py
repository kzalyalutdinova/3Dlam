# Generated by Django 5.0.6 on 2024-07-02 09:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mycalendar', '0005_alter_day_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='day',
            name='date',
            field=models.DateField(editable=False, verbose_name='Date'),
        ),
    ]
