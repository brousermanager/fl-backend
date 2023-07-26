# Generated by Django 4.0.1 on 2023-07-26 17:53

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('insert_time', models.TimeField(auto_now_add=True)),
                ('update_time', models.TimeField(auto_now=True)),
                ('cover', models.ImageField(blank=True, null=True, upload_to='images/Collection')),
            ],
        ),
    ]