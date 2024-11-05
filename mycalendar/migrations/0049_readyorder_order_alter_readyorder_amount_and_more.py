# Generated by Django 5.0.6 on 2024-11-05 09:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mycalendar', '0048_readyorder_regularorder_remove_printingplan_material_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='readyorder',
            name='order',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='mycalendar.order'),
        ),
        migrations.AlterField(
            model_name='readyorder',
            name='amount',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='Amount of details'),
        ),
        migrations.DeleteModel(
            name='RODrawing',
        ),
    ]
