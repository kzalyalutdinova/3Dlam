# Generated by Django 5.0.6 on 2024-09-04 07:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mycalendar', '0021_material'),
    ]

    operations = [
        migrations.CreateModel(
            name='Printer',
            fields=[
                ('sn', models.AutoField(primary_key=True, serialize=False)),
                ('model', models.CharField(max_length=20, verbose_name='The printer model')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200, verbose_name='The name of the order')),
                ('amount', models.PositiveSmallIntegerField(default=1, verbose_name='Amount of details to produce')),
                ('material', models.CharField(max_length=20, verbose_name='Material')),
                ('cost', models.PositiveIntegerField(verbose_name='Order cost')),
                ('customer', models.CharField(max_length=200, verbose_name='The name of the order')),
                ('ready', models.BooleanField(default=False, verbose_name='Is the order ready?')),
                ('comment', models.CharField(max_length=300, verbose_name='Comment')),
                ('date', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='mycalendar.monthyear')),
            ],
        ),
        migrations.CreateModel(
            name='PrintingRegister',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('duration', models.DurationField(verbose_name='Order completion time')),
                ('date_start', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='mycalendar.day')),
                ('order', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='mycalendar.order')),
                ('printer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='mycalendar.printer')),
            ],
        ),
    ]
