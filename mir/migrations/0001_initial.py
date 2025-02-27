# Generated by Django 5.1.6 on 2025-02-22 16:50

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('url', models.URLField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Document',
                'verbose_name_plural': 'Documents',
                'default_related_name': 'documents',
            },
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('employee_id', models.CharField(blank=True, max_length=255, null=True)),
                ('first_name', models.CharField(blank=True, max_length=255, null=True)),
                ('last_name', models.CharField(blank=True, max_length=255, null=True)),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('email', models.EmailField(blank=True, max_length=255, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Employee',
                'verbose_name_plural': 'Employees',
                'default_related_name': 'employees',
            },
        ),
        migrations.CreateModel(
            name='Risk',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(help_text='Enter a short and descriptive name for the risk.', max_length=255, verbose_name='Name')),
                ('description', models.TextField(help_text='Provide a detailed description of the risk.', verbose_name='Description')),
                ('url', models.URLField(blank=True, help_text='URL for this risk', null=True, verbose_name='URL')),
                ('category', models.CharField(choices=[('operational', 'Operational'), ('financial', 'Financial'), ('compliance', 'Compliance'), ('strategic', 'Strategic'), ('reputational', 'Reputational')], help_text='Select the category that best describes this risk.', max_length=50, verbose_name='Category')),
                ('inherent_impact', models.CharField(choices=[('very-low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')], help_text='Assess the impact level of the risk before any mitigation actions.', max_length=10, verbose_name='Inherent Impact')),
                ('inherent_likelihood', models.CharField(choices=[('rare', 'Rare'), ('unlikely', 'Unlikely'), ('possible', 'Possible'), ('likely', 'Likely'), ('almost-certain', 'Almost Certain')], help_text='Assess the likelihood of the risk occurring before any mitigation actions.', max_length=15, verbose_name='Inherent Likelihood')),
                ('mitigation_plan', models.TextField(blank=True, help_text='Describe the mitigation strategies or actions to reduce the risk.', null=True, verbose_name='Mitigation Plan')),
                ('residual_impact', models.CharField(blank=True, choices=[('very-low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')], help_text='Assess the impact level of the risk after mitigation actions.', max_length=10, null=True, verbose_name='Residual Impact')),
                ('residual_likelihood', models.CharField(blank=True, choices=[('rare', 'Rare'), ('unlikely', 'Unlikely'), ('possible', 'Possible'), ('likely', 'Likely'), ('almost-certain', 'Almost Certain')], help_text='Assess the likelihood of the risk occurring after mitigation actions.', max_length=15, null=True, verbose_name='Residual Likelihood')),
                ('responsible_party_name', models.CharField(help_text='Specify the name of the individual or department responsible for managing this risk.', max_length=255, verbose_name='Name of responsible party')),
                ('status', models.CharField(choices=[('identified', 'Identified'), ('assessed', 'Assessed'), ('mitigated', 'Mitigated'), ('resolved', 'Resolved'), ('accepted', 'Accepted')], default='identified', help_text='Track the current status of the risk in its lifecycle.', max_length=20, verbose_name='Status')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Training',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Training',
                'verbose_name_plural': 'Trainings',
                'default_related_name': 'trainings',
            },
        ),
        migrations.CreateModel(
            name='TrainingAttended',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('date', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Training attended',
                'verbose_name_plural': 'Trainings attended',
                'default_related_name': 'trainings_attended',
            },
        ),
        migrations.CreateModel(
            name='TrainingOrganized',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('date', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Training organized',
                'verbose_name_plural': 'Trainings organized',
                'default_related_name': 'trainings_organized',
            },
        ),
        migrations.CreateModel(
            name='UUIDTaggedItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.UUIDField(db_index=True, verbose_name='object ID')),
            ],
            options={
                'verbose_name': 'Tag',
                'verbose_name_plural': 'Tags',
            },
        ),
    ]
