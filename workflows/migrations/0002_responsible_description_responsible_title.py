# Generated by Django 5.1.4 on 2025-01-26 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workflows', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='responsible',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='responsible',
            name='title',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
