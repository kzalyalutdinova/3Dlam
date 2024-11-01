# Generated by Django 5.0.6 on 2024-11-01 11:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mycalendar', '0047_alter_printingplan_options_printingplan_hidden'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReadyOrder',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('amount', models.PositiveSmallIntegerField(default=1, verbose_name='Amount of details')),
                ('comments', models.CharField(blank=True, max_length=200, verbose_name='Comments on packing')),
                ('ready', models.BooleanField(default=False, verbose_name='Is it ready?')),
            ],
            options={
                'verbose_name': 'Ready order',
                'verbose_name_plural': 'Ready orders',
            },
        ),
        migrations.CreateModel(
            name='RegularOrder',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, verbose_name='The name of the order')),
                ('comments', models.CharField(blank=True, max_length=200, verbose_name='Comments on packing')),
                ('amount', models.PositiveSmallIntegerField(default=1, verbose_name='Amount of details')),
                ('ready', models.BooleanField(default=False, verbose_name='Is it ready?')),
            ],
        ),
        migrations.RemoveField(
            model_name='printingplan',
            name='material',
        ),
        migrations.AddField(
            model_name='printingplan',
            name='orders',
            field=models.ManyToManyField(blank=True, to='mycalendar.order'),
        ),
        migrations.CreateModel(
            name='RODrawing',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('file', models.ImageField(max_length=1000, upload_to='printing_plan/ready_orders/', verbose_name='Drawing for printing plan')),
                ('pp', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='mycalendar.readyorder')),
            ],
        ),
    ]
