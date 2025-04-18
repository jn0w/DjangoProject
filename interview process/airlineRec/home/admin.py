from django.contrib import admin
from .models import User, Skill, Candidate, CandidateSkill, JobPosting, Application, JobInterview

class CandidateAdmin(admin.ModelAdmin):
    list_display = ('user', 'experience_years', 'education_institution', 'education_degree')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'education_institution')
    list_filter = ('education_currently_studying',)
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'resume', 'experience_years')
        }),
        ('Education', {
            'fields': ('education_institution', 'education_degree', 'education_field', 
                      'education_start_year', 'education_end_year', 'education_currently_studying')
        }),
        ('Additional Information', {
            'fields': ('certifications',)
        }),
    )

# Register your models here
admin.site.register(User)
admin.site.register(Skill)
admin.site.register(Candidate, CandidateAdmin)
admin.site.register(CandidateSkill)
admin.site.register(JobPosting)
admin.site.register(Application)
admin.site.register(JobInterview)
