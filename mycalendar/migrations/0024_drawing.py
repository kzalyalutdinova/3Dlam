# Generated by Django 5.0.6 on 2024-09-06 09:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mycalendar', '0023_alter_order_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='Drawing',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('file', models.ImageField(max_length=1000, upload_to='uploads/', verbose_name='Drawing for detail ordered')),
                ('order', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='mycalendar.order')),
            ],
        ),
    ]
