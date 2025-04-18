from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    CANDIDATE = 'candidate'
    HR_COORDINATOR = 'hr_coordinator'
    INTERVIEWER = 'interviewer'
    
    ROLE_CHOICES = [
        (CANDIDATE, 'Candidate'),
        (HR_COORDINATOR, 'HR Coordinator'),
        (INTERVIEWER, 'Interviewer'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=CANDIDATE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class Skill(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Candidate(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='candidate_profile')
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    skills = models.ManyToManyField(Skill, through='CandidateSkill')
    experience_years = models.PositiveIntegerField(default=0)
    
    # Education fields
    education_institution = models.CharField(max_length=200, blank=True, null=True)
    education_degree = models.CharField(max_length=100, blank=True, null=True)
    education_field = models.CharField(max_length=100, blank=True, null=True)
    education_start_year = models.PositiveIntegerField(blank=True, null=True)
    education_end_year = models.PositiveIntegerField(blank=True, null=True)
    education_currently_studying = models.BooleanField(default=False)
    
    # Certifications
    certifications = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

class CandidateSkill(models.Model):
    BEGINNER = 'beginner'
    INTERMEDIATE = 'intermediate'
    ADVANCED = 'advanced'
    EXPERT = 'expert'
    
    PROFICIENCY_CHOICES = [
        (BEGINNER, 'Beginner'),
        (INTERMEDIATE, 'Intermediate'),
        (ADVANCED, 'Advanced'),
        (EXPERT, 'Expert'),
    ]
    
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    proficiency = models.CharField(max_length=15, choices=PROFICIENCY_CHOICES, default=BEGINNER)
    years_experience = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ('candidate', 'skill')
    
    def __str__(self):
        return f"{self.candidate} - {self.skill} ({self.get_proficiency_display()})"

class JobPosting(models.Model):
    title = models.CharField(max_length=100)
    department = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    requirements = models.TextField(null=True, blank=True)
    salary_range = models.CharField(max_length=50, blank=True, null=True)
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_postings', null=True)
    posted_date = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title

class JobApplication(models.Model):
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    cover_letter = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending Review'),
        ('reviewing', 'Under Review'),
        ('interview', 'Interview Stage'),
        ('offered', 'Job Offered'),
        ('rejected', 'Application Rejected'),
        ('withdrawn', 'Application Withdrawn'),
    ], default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.candidate.user.username} - {self.job.title}"

class Application(models.Model):
    APPLIED = 'applied'
    SCREENING = 'screening'
    INTERVIEWING = 'interviewing'
    OFFERED = 'offered'
    REJECTED = 'rejected'
    ACCEPTED = 'accepted'
    
    STATUS_CHOICES = [
        (APPLIED, 'Applied'),
        (SCREENING, 'Screening'),
        (INTERVIEWING, 'Interviewing'),
        (OFFERED, 'Offered'),
        (REJECTED, 'Rejected'),
        (ACCEPTED, 'Accepted'),
    ]
    
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='applications')
    job_posting = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=APPLIED)
    application_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ('candidate', 'job_posting')
    
    def __str__(self):
        return f"{self.candidate} - {self.job_posting} ({self.get_status_display()})"

class JobInterview(models.Model):
    """Interview model linked to job applications"""
    application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name='interviews')
    hr_coordinator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interviews')
    interviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conducted_interviews', null=True, blank=True)
    scheduled_date = models.DateTimeField()
    location = models.CharField(max_length=100, blank=True)
    is_online = models.BooleanField(default=False)
    meeting_link = models.CharField(max_length=255, blank=True, null=True)  # Changed from URLField
    status = models.CharField(max_length=20, choices=[
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rescheduled', 'Rescheduled')
    ], default='scheduled')
    feedback = models.TextField(blank=True)
    interviewer_feedback = models.TextField(blank=True)
    rating = models.PositiveSmallIntegerField(blank=True, null=True)  # 1-5 rating
    interviewer_rating = models.PositiveSmallIntegerField(blank=True, null=True)  # 1-5 rating from interviewer
    
    def __str__(self):
        return f"Interview for {self.application.candidate.user.get_full_name()} - {self.application.job.title}"

class Education(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='educations')
    institution = models.CharField(max_length=200)
    degree = models.CharField(max_length=100)
    field_of_study = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-end_date', '-start_date']
        
    def __str__(self):
        return f"{self.degree} in {self.field_of_study} at {self.institution}"
