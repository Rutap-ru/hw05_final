# Generated by Django 2.2.9 on 2020-12-01 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_auto_20201201_1403'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='slug',
            field=models.SlugField(unique=True, verbose_name='уникальный адрес группы'),
        ),
    ]