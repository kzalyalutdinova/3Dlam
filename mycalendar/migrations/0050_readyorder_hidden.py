# Generated by Django 5.0.6 on 2024-11-05 11:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mycalendar', '0049_readyorder_order_alter_readyorder_amount_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='readyorder',
            name='hidden',
            field=models.BooleanField(default=False, verbose_name='Is it hidden in the table'),
        ),
    ]
