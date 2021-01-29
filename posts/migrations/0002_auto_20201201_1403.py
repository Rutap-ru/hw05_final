# Generated by Django 2.2.9 on 2020-12-01 07:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='название гуппы')),
                ('slug', models.CharField(max_length=200, unique=True, verbose_name='уникальный адрес группы')),
                ('description', models.TextField(verbose_name='описание группы')),
            ],
        ),
        migrations.AddField(
            model_name='post',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='Groups', to='posts.Group'),
        ),
    ]
