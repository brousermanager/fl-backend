# Generated by Django 4.0.1 on 2024-03-21 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('podcast', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='podcast',
            name='cover',
            field=models.URLField(blank=True, null=True),
        ),
    ]
