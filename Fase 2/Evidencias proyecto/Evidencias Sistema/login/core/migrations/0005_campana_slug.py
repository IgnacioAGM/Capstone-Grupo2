# Generated by Django 5.1.2 on 2024-11-09 01:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_campana_monto_donado'),
    ]

    operations = [
        migrations.AddField(
            model_name='campana',
            name='slug',
            field=models.SlugField(blank=True, unique=True),
        ),
    ]
