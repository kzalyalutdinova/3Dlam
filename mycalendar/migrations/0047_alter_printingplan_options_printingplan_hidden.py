# Generated by Django 5.0.6 on 2024-10-28 09:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mycalendar', '0046_alter_printingplan_datetime_end_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='printingplan',
            options={'ordering': ['id'], 'verbose_name': 'Printing Plan', 'verbose_name_plural': 'Printing Plan'},
        ),
        migrations.AddField(
            model_name='printingplan',
            name='hidden',
            field=models.BooleanField(default=False, verbose_name='Is it hidden in the table'),
        ),
    ]