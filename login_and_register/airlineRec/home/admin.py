from django.contrib import admin
from .models import User, Skill, Candidate, CandidateSkill, JobPosting, Application, Interview, Assessment, Onboarding, OnboardingTask

# Register your models here
admin.site.register(User)
admin.site.register(Skill)
admin.site.register(Candidate)
admin.site.register(CandidateSkill)
admin.site.register(JobPosting)
admin.site.register(Application)

admin.site.register(Interview)
admin.site.register(Assessment)
admin.site.register(Onboarding)
admin.site.register(OnboardingTask)
