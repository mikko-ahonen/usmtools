# Generated by Django 5.1.6 on 2025-02-28 00:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('xref', '0003_crossreference_description'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='crossreference',
            name='domain',
        ),
    ]
