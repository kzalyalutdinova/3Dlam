# Generated by Django 5.0.6 on 2024-10-18 09:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mycalendar', '0042_alter_printingplan_options_alter_printingplan_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='printingplan',
            name='priority',
            field=models.CharField(choices=[('1', '1-й приоритет'), ('2', '2-й приоритет'), ('3', '3-й приоритет'), ('0', 'Термичка')], max_length=1, verbose_name='Priority'),
        ),
    ]
