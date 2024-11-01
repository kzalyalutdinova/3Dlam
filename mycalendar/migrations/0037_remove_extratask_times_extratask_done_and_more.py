# Generated by Django 5.0.6 on 2024-10-11 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mycalendar', '0036_extratask_times'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='extratask',
            name='times',
        ),
        migrations.AddField(
            model_name='extratask',
            name='done',
            field=models.BooleanField(default=False, verbose_name='Is the task done?'),
        ),
        migrations.AlterField(
            model_name='todo',
            name='times',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='Number of times the task has been done'),
        ),
    ]
