# Generated by Django 5.1.7 on 2025-03-18 18:08

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0005_remove_jobposting_closing_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobapplication',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending Review'), ('reviewing', 'Under Review'), ('interview', 'Interview Stage'), ('offered', 'Job Offered'), ('rejected', 'Application Rejected'), ('withdrawn', 'Application Withdrawn')], default='pending', max_length=20),
        ),
        migrations.CreateModel(
            name='JobInterview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scheduled_date', models.DateTimeField()),
                ('location', models.CharField(blank=True, max_length=100)),
                ('is_online', models.BooleanField(default=False)),
                ('meeting_link', models.URLField(blank=True, null=True)),
                ('status', models.CharField(choices=[('scheduled', 'Scheduled'), ('completed', 'Completed'), ('cancelled', 'Cancelled'), ('rescheduled', 'Rescheduled')], default='scheduled', max_length=20)),
                ('feedback', models.TextField(blank=True)),
                ('rating', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('application', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interviews', to='home.jobapplication')),
                ('recruiter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interviews', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='Interview',
        ),
    ]
