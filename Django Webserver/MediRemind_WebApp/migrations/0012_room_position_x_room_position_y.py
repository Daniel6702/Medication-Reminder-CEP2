# Generated by Django 5.0.3 on 2024-04-26 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MediRemind_WebApp', '0011_auto_20240425_0711'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='position_x',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='room',
            name='position_y',
            field=models.FloatField(default=0.0),
        ),
    ]
