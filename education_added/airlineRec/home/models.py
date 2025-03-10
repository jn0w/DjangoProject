from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    RECRUITER = 'recruiter'
    CANDIDATE = 'candidate'
    DEPARTMENT_MANAGER = 'department_manager'
    HR_COORDINATOR = 'hr_coordinator'
    
    ROLE_CHOICES = [
        (RECRUITER, 'Recruiter'),
        (CANDIDATE, 'Candidate'),
        (DEPARTMENT_MANAGER, 'Department Manager'),
        (HR_COORDINATOR, 'HR Coordinator'),
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
    OPEN = 'open'
    CLOSED = 'closed'
    
    STATUS_CHOICES = [
        (OPEN, 'Open'),
        (CLOSED, 'Closed'),
    ]
    
    title = models.CharField(max_length=100)
    description = models.TextField()
    department = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=OPEN)
    required_skills = models.ManyToManyField(Skill)
    posted_date = models.DateTimeField(auto_now_add=True)
    closing_date = models.DateField()
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_postings')
    
    def __str__(self):
        return f"{self.title} ({self.department})"

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

class Interview(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='interviews')
    interviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conducted_interviews')
    scheduled_date = models.DateTimeField()
    location = models.CharField(max_length=100, blank=True)  # Or online
    is_online = models.BooleanField(default=False)
    meeting_link = models.URLField(blank=True, null=True)  # For online interviews
    status = models.CharField(max_length=20, choices=[
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rescheduled', 'Rescheduled')
    ], default='scheduled')
    feedback = models.TextField(blank=True)
    rating = models.PositiveSmallIntegerField(blank=True, null=True)  # 1-5 rating
    
    def __str__(self):
        return f"Interview: {self.application.candidate} for {self.application.job_posting}"

class Assessment(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='assessments')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    evaluator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='evaluations')
    score = models.PositiveSmallIntegerField()  # 1-100 score
    feedback = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Assessment: {self.candidate} - {self.skill}"

class Onboarding(models.Model):
    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='onboarding')
    hr_coordinator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='managed_onboardings')
    start_date = models.DateField()
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('terminated', 'Terminated')
    ], default='pending')
    
    def __str__(self):
        return f"Onboarding: {self.application.candidate}"

class OnboardingTask(models.Model):
    onboarding = models.ForeignKey(Onboarding, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=100)
    description = models.TextField()
    due_date = models.DateField()
    is_completed = models.BooleanField(default=False)
    completed_date = models.DateField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.title} for {self.onboarding.application.candidate}"

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
