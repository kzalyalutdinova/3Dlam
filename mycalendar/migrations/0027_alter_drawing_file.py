# Generated by Django 5.0.6 on 2024-09-12 10:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mycalendar', '0026_printingregister_month_printingregister_year'),
    ]

    operations = [
        migrations.AlterField(
            model_name='drawing',
            name='file',
            field=models.ImageField(max_length=1000, upload_to='uploads/<django.db.models.fields.related.ForeignKey>', verbose_name='Drawing for detail ordered'),
        ),
    ]
