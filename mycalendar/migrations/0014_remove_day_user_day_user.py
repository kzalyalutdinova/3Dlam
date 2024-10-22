# Generated by Django 5.0.6 on 2024-07-15 11:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mycalendar', '0013_day_edited'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='day',
            name='user',
        ),
        migrations.AddField(
            model_name='day',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='mycalendar.user'),
        ),
    ]
