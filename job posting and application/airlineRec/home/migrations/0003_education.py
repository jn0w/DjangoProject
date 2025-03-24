# Generated by Django 5.1.7 on 2025-03-09 19:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_assessment_interview_onboarding_onboardingtask'),
    ]

    operations = [
        migrations.CreateModel(
            name='Education',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('institution', models.CharField(max_length=200)),
                ('degree', models.CharField(max_length=100)),
                ('field_of_study', models.CharField(max_length=100)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(blank=True, null=True)),
                ('is_current', models.BooleanField(default=False)),
                ('description', models.TextField(blank=True)),
                ('candidate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='educations', to='home.candidate')),
            ],
            options={
                'ordering': ['-end_date', '-start_date'],
            },
        ),
    ]
