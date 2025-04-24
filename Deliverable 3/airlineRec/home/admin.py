from django.contrib import admin
from .models import User, Skill, Candidate, CandidateSkill, JobPosting, Application, JobInterview

# Custom admin configuration for the Candidate model
class CandidateAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = ('user', 'experience_years', 'education_institution', 'education_degree')
    
    # Fields that can be searched
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'education_institution')
    
    # Add filter options on the right sidebar
    list_filter = ('education_currently_studying',)
    
    # Organize edit form into sections
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

# Register models to make them accessible in the admin interface
admin.site.register(User)
admin.site.register(Skill)
admin.site.register(Candidate, CandidateAdmin)  # Register with custom admin configuration
admin.site.register(CandidateSkill)
admin.site.register(JobPosting)
admin.site.register(Application)
admin.site.register(JobInterview)
