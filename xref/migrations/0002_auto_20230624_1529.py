# Generated by Django 3.1.14 on 2023-06-24 15:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('xref', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='statement',
            name='requirement',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='statements', to='xref.requirement'),
        ),
        migrations.AlterField(
            model_name='statementtosubstatement',
            name='statement',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='xref.statement'),
        ),
        migrations.AlterField(
            model_name='statementtosubstatement',
            name='substatement',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='xref.substatement'),
        ),
    ]
