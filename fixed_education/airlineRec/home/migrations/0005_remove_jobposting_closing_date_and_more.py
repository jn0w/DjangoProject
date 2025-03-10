# Generated by Django 5.1.7 on 2025-03-10 19:17

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_remove_candidate_education_candidate_certifications_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='jobposting',
            name='closing_date',
        ),
        migrations.RemoveField(
            model_name='jobposting',
            name='required_skills',
        ),
        migrations.RemoveField(
            model_name='jobposting',
            name='status',
        ),
        migrations.AddField(
            model_name='jobposting',
            name='deadline',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='jobposting',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='jobposting',
            name='location',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='jobposting',
            name='requirements',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='jobposting',
            name='salary_range',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='jobposting',
            name='department',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='jobposting',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='jobposting',
            name='posted_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='job_postings', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='JobApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cover_letter', models.TextField(blank=True, null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending Review'), ('reviewing', 'Under Review'), ('interview', 'Interview Stage'), ('offered', 'Job Offered'), ('rejected', 'Application Rejected')], default='pending', max_length=20)),
                ('applied_at', models.DateTimeField(auto_now_add=True)),
                ('candidate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.candidate')),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.jobposting')),
            ],
        ),
    ]
