# Generated by Django 5.0.6 on 2024-10-11 11:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mycalendar', '0035_extratask'),
    ]

    operations = [
        migrations.AddField(
            model_name='extratask',
            name='times',
            field=models.PositiveSmallIntegerField(default=1, verbose_name='Number of times the task has been done'),
        ),
    ]
