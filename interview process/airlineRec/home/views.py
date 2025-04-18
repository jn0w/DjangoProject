from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, CandidateSkillForm, SkillSearchForm, EducationForm, CandidateEducationForm, JobPostingForm, JobApplicationForm, CandidateResumeForm, JobInterviewForm, InterviewFeedbackForm, ApplicationStatusForm, InterviewerFeedbackForm, JobOfferResponseForm, StaffRegisterForm
from .models import User, Candidate, Skill, CandidateSkill, Education, JobPosting, JobApplication, JobInterview
from django.contrib.auth import logout
from datetime import datetime
from django.utils import timezone

def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username} as a Candidate! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})

@login_required
def profile(request):
    # Get the candidate profile if the user is a candidate
    candidate = None
    candidate_skills = []
    
    if request.user.role == 'candidate':
        candidate, created = Candidate.objects.get_or_create(user=request.user)
        candidate_skills = CandidateSkill.objects.filter(candidate=candidate)
    
    context = {
        'candidate': candidate,
        'candidate_skills': candidate_skills,
    }
    
    return render(request, 'profile.html', context)

@login_required
def manage_skills(request):
    # Ensure user is a candidate
    if request.user.role != 'candidate':
        messages.error(request, "Only candidates can access this page.")
        return redirect('home')
    
    # Get or create candidate profile
    candidate, created = Candidate.objects.get_or_create(user=request.user)
    candidate_skills = CandidateSkill.objects.filter(candidate=candidate)
    
    # Initialize search form for skills
    search_form = SkillSearchForm(request.GET)
    skills = []
    
    if search_form.is_valid() and search_form.cleaned_data.get('query'):
        query = search_form.cleaned_data.get('query')
        skills = Skill.objects.filter(name__icontains=query)
    
    if request.method == 'POST':
        if 'add_skill' in request.POST:
            # Handle skill addition
            skill_form = CandidateSkillForm(request.POST)
            if skill_form.is_valid():
                skill = skill_form.cleaned_data['skill']
                
                # Check if skill already exists for candidate
                if CandidateSkill.objects.filter(candidate=candidate, skill=skill).exists():
                    messages.warning(request, f'You already have "{skill.name}" in your skills list.')
                else:
                    candidate_skill = skill_form.save(commit=False)
                    candidate_skill.candidate = candidate
                    candidate_skill.save()
                    messages.success(request, f'Added "{skill.name}" to your skills!')
                
                return redirect('manage_skills')
                
        elif 'update_education' in request.POST:
            # Handle education update - make sure all fields are captured
            candidate.education_institution = request.POST.get('education_institution', '')
            candidate.education_degree = request.POST.get('education_degree', '')
            candidate.education_field = request.POST.get('education_field', '')
            
            # Handle start year (convert to integer if present)
            start_year = request.POST.get('education_start_year', '')
            if start_year and start_year.isdigit():
                candidate.education_start_year = int(start_year)
            
            # Handle "currently studying" checkbox
            candidate.education_currently_studying = 'education_currently_studying' in request.POST
            
            # Handle end year (convert to integer if present and not currently studying)
            if not candidate.education_currently_studying:
                end_year = request.POST.get('education_end_year', '')
                if end_year and end_year.isdigit():
                    candidate.education_end_year = int(end_year)
            else:
                candidate.education_end_year = None
            
            # Handle certifications
            candidate.certifications = request.POST.get('certifications', '')
            
            # Save all changes
            candidate.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('manage_skills')
        
        elif 'update_resume' in request.POST:
            # Handle resume upload
            resume_form = CandidateResumeForm(request.POST, request.FILES, instance=candidate)
            if resume_form.is_valid():
                resume_form.save()
                messages.success(request, 'Resume uploaded successfully!')
                return redirect('manage_skills')
    else:
        skill_form = CandidateSkillForm()
        resume_form = CandidateResumeForm(instance=candidate)
    
    context = {
        'candidate': candidate,
        'candidate_skills': candidate_skills,
        'search_form': search_form,
        'skills': skills,
        'skill_form': skill_form,
        'resume_form': resume_form,
        'all_skills': Skill.objects.all()
    }
    return render(request, 'manage_skills.html', context)

@login_required
def delete_skill(request, skill_id):
    # Ensure user is a candidate
    if request.user.role != 'candidate':
        messages.error(request, "Only candidates can access this page.")
        return redirect('home')
    
    # Get candidate profile
    candidate = get_object_or_404(Candidate, user=request.user)
    
    # Get the candidate skill
    candidate_skill = get_object_or_404(CandidateSkill, id=skill_id, candidate=candidate)
    
    skill_name = candidate_skill.skill.name
    candidate_skill.delete()
    messages.success(request, f'Removed "{skill_name}" from your skills.')
    
    return redirect('manage_skills')

def logout_view(request):
    logout(request)
    return redirect('/')  # Direct redirect to homepage URL

@login_required
def education_list(request):
    # Ensure user is a candidate
    if request.user.role != 'candidate':
        messages.error(request, "Only candidates can access this page.")
        return redirect('home')
    
    # Get candidate profile
    candidate, created = Candidate.objects.get_or_create(user=request.user)
    
    # Get education entries
    educations = Education.objects.filter(candidate=candidate)
    
    context = {
        'educations': educations
    }
    return render(request, 'education_list.html', context)

@login_required
def add_education(request):
    # Ensure user is a candidate
    if request.user.role != 'candidate':
        messages.error(request, "Only candidates can access this page.")
        return redirect('home')
    
    # Get candidate profile
    candidate, created = Candidate.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = EducationForm(request.POST)
        if form.is_valid():
            education = form.save(commit=False)
            education.candidate = candidate
            education.save()
            messages.success(request, "Education added successfully!")
            return redirect('education_list')
    else:
        form = EducationForm()
    
    context = {
        'form': form,
        'title': 'Add Education'
    }
    return render(request, 'education_form.html', context)

@login_required
def edit_education(request, education_id):
    # Ensure user is a candidate
    if request.user.role != 'candidate':
        messages.error(request, "Only candidates can access this page.")
        return redirect('home')
    
    # Get candidate profile
    candidate, created = Candidate.objects.get_or_create(user=request.user)
    
    # Get education entry
    education = get_object_or_404(Education, id=education_id, candidate=candidate)
    
    if request.method == 'POST':
        form = EducationForm(request.POST, instance=education)
        if form.is_valid():
            form.save()
            messages.success(request, "Education updated successfully!")
            return redirect('education_list')
    else:
        form = EducationForm(instance=education)
    
    context = {
        'form': form,
        'title': 'Edit Education'
    }
    return render(request, 'education_form.html', context)

@login_required
def delete_education(request, education_id):
    # Ensure user is a candidate
    if request.user.role != 'candidate':
        messages.error(request, "Only candidates can access this page.")
        return redirect('home')
    
    # Get candidate profile
    candidate, created = Candidate.objects.get_or_create(user=request.user)
    
    # Get education entry
    education = get_object_or_404(Education, id=education_id, candidate=candidate)
    
    if request.method == 'POST':
        education.delete()
        messages.success(request, "Education deleted successfully!")
        return redirect('education_list')
    
    context = {
        'education': education
    }
    return render(request, 'education_confirm_delete.html', context)

@login_required
def job_list(request):
    """View all available job postings"""
    jobs = JobPosting.objects.filter(is_active=True).order_by('-posted_date')
    
    # Check for role-specific actions
    is_hr = request.user.role == 'hr_coordinator'
    
    return render(request, 'job_list.html', {
        'jobs': jobs,
        'is_hr': is_hr
    })

@login_required
def job_detail(request, job_id):
    """View details of a specific job"""
    job = get_object_or_404(JobPosting, pk=job_id)
    
    # Check if user is a candidate and has already applied
    has_applied = False
    if request.user.role == 'candidate':
        try:
            candidate = Candidate.objects.get(user=request.user)
            has_applied = JobApplication.objects.filter(job=job, candidate=candidate).exists()
        except Candidate.DoesNotExist:
            # Handle case where user is a candidate but doesn't have a candidate profile
            pass
    
    return render(request, 'job_detail.html', {
        'job': job,
        'has_applied': has_applied
    })

@login_required
def create_job(request):
    # Ensure user is an HR Coordinator
    if request.user.role != 'hr_coordinator':
        messages.error(request, "Only HR Coordinators can post job listings.")
        return redirect('home')
    
    if request.method == 'POST':
        form = JobPostingForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            messages.success(request, f"Job '{job.title}' posted successfully!")
            return redirect('job_detail', job_id=job.id)
    else:
        form = JobPostingForm()
    
    context = {
        'form': form,
        'title': 'Post a New Job'
    }
    return render(request, 'create_job.html', context)

@login_required
def delete_job(request, job_id):
    """Delete a job posting (HR Coordinator only)"""
    # Ensure user is an HR Coordinator
    if request.user.role != 'hr_coordinator':
        messages.error(request, "Only HR Coordinators can delete job listings.")
        return redirect('home')
    
    job = get_object_or_404(JobPosting, pk=job_id)
    
    # Check if there are any applications for this job
    has_applications = JobApplication.objects.filter(job=job).exists()
    
    if request.method == 'POST':
        if has_applications and not request.POST.get('confirm_with_applications'):
            # If there are applications but the user hasn't confirmed deletion with applications
            messages.error(request, "This job posting has applications. Please confirm deletion.")
            return redirect('delete_job', job_id=job.id)
        
        job_title = job.title
        job.delete()
        messages.success(request, f"Job posting '{job_title}' has been deleted successfully.")
        return redirect('job_list')
    
    context = {
        'job': job,
        'has_applications': has_applications
    }
    return render(request, 'delete_job_confirm.html', context)

@login_required
def apply_for_job(request, job_id):
    # Ensure user is a candidate
    if request.user.role != 'candidate':
        messages.error(request, "Only candidates can apply for jobs.")
        return redirect('job_list')
    
    job = get_object_or_404(JobPosting, pk=job_id)
    
    # Try to get candidate profile
    try:
        candidate = Candidate.objects.get(user=request.user)
    except Candidate.DoesNotExist:
        messages.error(request, "Candidate profile not found.")
        return redirect('job_list')
    
    # Check if already applied
    if JobApplication.objects.filter(job=job, candidate=candidate).exists():
        messages.info(request, "You have already applied for this job.")
        return redirect('job_detail', job_id=job_id)
    
    if request.method == 'POST':
        form = JobApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.candidate = candidate
            application.save()
            messages.success(request, f"You have successfully applied for {job.title}!")
            return redirect('job_list')
    else:
        form = JobApplicationForm()
    
    context = {
        'job': job,
        'form': form
    }
    
    # Make sure we're rendering the template, not redirecting
    return render(request, 'apply_for_job.html', context)

@login_required
def application_list(request):
    """View all job applications (HR Coordinator only)"""
    # Ensure user is an HR Coordinator
    if request.user.role != 'hr_coordinator' and not request.user.is_superuser:
        messages.error(request, "Access denied. HR Coordinator access required.")
        return redirect('home')
    
    # Get filter parameters
    job_id = request.GET.get('job_id')
    status = request.GET.get('status')
    
    # Start with all applications
    applications = JobApplication.objects.select_related('job', 'candidate__user').all()
    
    # Apply filters if provided
    if job_id:
        applications = applications.filter(job_id=job_id)
    if status:
        applications = applications.filter(status=status)
    
    # Order by most recent first
    applications = applications.order_by('-applied_at')
    
    # Get all jobs for the filter dropdown
    jobs = JobPosting.objects.all()
    
    context = {
        'applications': applications,
        'jobs': jobs,
        'current_job_id': job_id,
        'current_status': status,
        'status_choices': JobApplication._meta.get_field('status').choices
    }
    
    return render(request, 'application_list.html', context)

@login_required
def application_detail(request, application_id):
    """View details of a specific job application (HR Coordinator only)"""
    # Ensure user is an HR Coordinator
    if request.user.role != 'hr_coordinator' and not request.user.is_superuser:
        messages.error(request, "Access denied. HR Coordinator access required.")
        return redirect('home')
    
    application = get_object_or_404(JobApplication.objects.select_related(
        'job', 'candidate__user'), pk=application_id)
    
    # Get candidate skills
    candidate_skills = CandidateSkill.objects.filter(candidate=application.candidate)
    
    # Get interviews for this application
    interviews = JobInterview.objects.filter(application=application).order_by('-scheduled_date')
    
    context = {
        'application': application,
        'candidate_skills': candidate_skills,
        'status_choices': JobApplication._meta.get_field('status').choices,
        'interviews': interviews
    }
    
    return render(request, 'application_detail.html', context)

@login_required
def update_application_status(request, application_id):
    """Update the status of a job application (HR Coordinator only)"""
    # Ensure user is an HR Coordinator
    if request.user.role != 'hr_coordinator' and not request.user.is_superuser:
        messages.error(request, "Access denied. HR Coordinator access required.")
        return redirect('home')
    
    application = get_object_or_404(JobApplication, pk=application_id)
    
    if request.method == 'POST':
        form = ApplicationStatusForm(request.POST, instance=application)
        if form.is_valid():
            old_status = application.status
            application = form.save()
            
            # If moving to interview stage, create an automatic interview assignment
            if application.status == 'interview' and form.cleaned_data['interviewer']:
                interviewer = form.cleaned_data['interviewer']
                
                # Check if there's already an interview for this application
                existing_interview = JobInterview.objects.filter(application=application).first()
                
                if not existing_interview:
                    # Create a default interview 7 days from now if none exists
                    interview_date = timezone.now() + timezone.timedelta(days=7)
                    JobInterview.objects.create(
                        application=application,
                        hr_coordinator=request.user,  # Current HR coordinator
                        interviewer=interviewer,
                        scheduled_date=interview_date,
                        status='scheduled'
                    )
                    messages.success(request, f"Application status updated to {application.get_status_display()} and interview assigned to {interviewer.get_full_name()}")
                else:
                    messages.success(request, f"Application status updated to {application.get_status_display()}. An interview is already scheduled.")
            else:
                messages.success(request, f"Application status updated to {application.get_status_display()}")
            
            # If moving from interview stage to another status, update interview status if needed
            if old_status == 'interview' and application.status != 'interview':
                interviews = JobInterview.objects.filter(application=application, status='scheduled')
                if interviews.exists():
                    for interview in interviews:
                        if application.status == 'rejected':
                            interview.status = 'cancelled'
                            interview.save()
                            messages.info(request, "The scheduled interview has been cancelled.")
            
            return redirect('application_detail', application_id=application_id)
    else:
        form = ApplicationStatusForm(instance=application)
    
    context = {
        'form': form,
        'application': application
    }
    
    return render(request, 'update_application_status.html', context)

@login_required
def my_applications(request):
    """View for candidates to see all their applications"""
    # Ensure user is a candidate
    if request.user.role != 'candidate':
        messages.error(request, "Access denied. Only candidates can view their applications.")
        return redirect('home')
    
    try:
        candidate = Candidate.objects.get(user=request.user)
        applications = JobApplication.objects.filter(candidate=candidate).select_related('job')
        
        context = {
            'applications': applications,
        }
        return render(request, 'my_applications.html', context)
    except Candidate.DoesNotExist:
        messages.error(request, "Candidate profile not found.")
        return redirect('home')

@login_required
def withdraw_application(request, application_id):
    """Allow candidates to withdraw their application"""
    # Ensure user is a candidate
    if request.user.role != 'candidate':
        messages.error(request, "Access denied. Only candidates can withdraw applications.")
        return redirect('home')
    
    try:
        candidate = Candidate.objects.get(user=request.user)
        application = get_object_or_404(JobApplication, id=application_id, candidate=candidate)
        
        if request.method == 'POST':
            # Get the job title for the success message
            job_title = application.job.title
            
            # Delete the application instead of marking it as withdrawn
            application.delete()
            messages.success(request, f"Your application for '{job_title}' has been withdrawn successfully. You may apply for this position again if you wish.")
            return redirect('my_applications')
        
        context = {
            'application': application,
        }
        return render(request, 'withdraw_confirmation.html', context)
    except Candidate.DoesNotExist:
        messages.error(request, "Candidate profile not found.")
        return redirect('home')

@login_required
def edit_application(request, application_id):
    """Allow candidates to edit their application cover letter"""
    # Ensure user is a candidate
    if request.user.role != 'candidate':
        messages.error(request, "Access denied. Only candidates can edit applications.")
        return redirect('home')
    
    try:
        candidate = Candidate.objects.get(user=request.user)
        application = get_object_or_404(JobApplication, id=application_id, candidate=candidate)
        
        # Don't allow editing if status is beyond initial stages
        if application.status not in ['pending', 'reviewing']:
            messages.warning(request, "This application cannot be edited because it's already in an advanced stage.")
            return redirect('my_applications')
        
        if request.method == 'POST':
            form = JobApplicationForm(request.POST, instance=application)
            if form.is_valid():
                form.save()
                messages.success(request, "Your application has been updated successfully.")
                return redirect('my_applications')
        else:
            form = JobApplicationForm(instance=application)
        
        context = {
            'form': form,
            'application': application,
        }
        return render(request, 'edit_application.html', context)
    except Candidate.DoesNotExist:
        messages.error(request, "Candidate profile not found.")
        return redirect('home')

@login_required
def interview_list(request):
    """View all interviews for HR coordinators or interviewers"""
    # Check if user is HR coordinator or interviewer
    if request.user.role not in ['hr_coordinator', 'interviewer']:
        messages.error(request, "Access denied. HR Coordinator or Interviewer access required.")
        return redirect('home')
    
    # Get filter parameters
    status = request.GET.get('status')
    
    # Filter interviews based on user role
    if request.user.role == 'interviewer':
        interviews = JobInterview.objects.filter(interviewer=request.user)
    else:  # HR Coordinator can see all interviews
        interviews = JobInterview.objects.all()
    
    # Apply status filter if provided
    if status:
        interviews = interviews.filter(status=status)
    
    # Order by scheduled date
    interviews = interviews.order_by('scheduled_date')
    
    context = {
        'interviews': interviews,
        'current_status': status,
        'status_choices': JobInterview._meta.get_field('status').choices
    }
    
    return render(request, 'interview_list.html', context)

@login_required
def schedule_interview(request, application_id):
    """Schedule an interview for a job application (HR Coordinator only)"""
    # Ensure user is an HR coordinator
    if request.user.role != 'hr_coordinator':
        messages.error(request, "Access denied. HR Coordinator access required.")
        return redirect('home')
    
    application = get_object_or_404(JobApplication, pk=application_id)
    
    if request.method == 'POST':
        form = JobInterviewForm(request.POST)
        if form.is_valid():
            interview = form.save(commit=False)
            interview.application = application
            interview.hr_coordinator = request.user
            interview.save()
            
            # Update application status to interview stage
            application.status = 'interview'
            application.save()
            
            messages.success(request, f"Interview for {application.candidate.user.get_full_name()} has been scheduled!")
            return redirect('interview_detail', interview_id=interview.id)
    else:
        form = JobInterviewForm()
    
    # Limit interviewer choices to users with interviewer role
    form.fields['interviewer'].queryset = User.objects.filter(role='interviewer')
    
    context = {
        'form': form,
        'application': application,
        'title': 'Schedule Interview'
    }
    
    return render(request, 'schedule_interview.html', context)

@login_required
def interview_detail(request, interview_id):
    """View details of a specific interview"""
    # Ensure user is an HR coordinator or interviewer
    if request.user.role not in ['hr_coordinator', 'interviewer']:
        messages.error(request, "Access denied. HR Coordinator or Interviewer access required.")
        return redirect('home')
    
    interview = get_object_or_404(JobInterview, pk=interview_id)
    
    # Check if user is the assigned HR coordinator or interviewer
    if request.user.role == 'hr_coordinator' and interview.hr_coordinator != request.user:
        messages.error(request, "Access denied. You are not assigned to this interview.")
        return redirect('interview_list')
    elif request.user.role == 'interviewer' and interview.interviewer != request.user:
        messages.error(request, "Access denied. You are not assigned to this interview.")
        return redirect('interview_list')
    
    context = {
        'interview': interview,
        'candidate': interview.application.candidate,
        'job': interview.application.job,
        'user': request.user,
    }
    
    return render(request, 'interview_detail.html', context)

@login_required
def update_interview(request, interview_id):
    """Update interview details (HR Coordinator only)"""
    # Ensure user is an HR coordinator
    if request.user.role != 'hr_coordinator':
        messages.error(request, "Access denied. HR Coordinator access required.")
        return redirect('home')
    
    interview = get_object_or_404(JobInterview, pk=interview_id)
    
    # Check if user is the assigned HR coordinator
    if interview.hr_coordinator != request.user:
        messages.error(request, "Access denied. You are not assigned to this interview.")
        return redirect('interview_list')
    
    if request.method == 'POST':
        form = JobInterviewForm(request.POST, instance=interview)
        if form.is_valid():
            form.save()
            messages.success(request, "Interview updated successfully!")
            return redirect('interview_detail', interview_id=interview.id)
    else:
        form = JobInterviewForm(instance=interview)
    
    # Limit interviewer choices to users with interviewer role
    form.fields['interviewer'].queryset = User.objects.filter(role='interviewer')
    
    context = {
        'form': form,
        'interview': interview,
        'title': 'Update Interview'
    }
    
    return render(request, 'schedule_interview.html', context)

@login_required
def interview_feedback(request, interview_id):
    """Submit feedback for a completed interview (HR Coordinator only)"""
    # Ensure user is an HR coordinator
    if request.user.role != 'hr_coordinator':
        messages.error(request, "Access denied. HR Coordinator access required.")
        return redirect('home')
    
    interview = get_object_or_404(JobInterview, pk=interview_id)
    
    # Check if user is the assigned HR coordinator
    if interview.hr_coordinator != request.user:
        messages.error(request, "Access denied. You are not assigned to this interview.")
        return redirect('interview_list')
    
    if request.method == 'POST':
        form = InterviewFeedbackForm(request.POST, instance=interview)
        if form.is_valid():
            interview = form.save(commit=False)
            interview.status = 'completed'  # Automatically mark as completed when feedback is submitted
            interview.save()
            messages.success(request, "Interview feedback submitted successfully!")
            
            # Update application status based on feedback
            application = interview.application
            # If rating is 4 or higher, move to next stage
            if interview.rating and interview.rating >= 4:
                application.status = 'offered'
                messages.success(request, "Candidate has been moved to Job Offer stage!")
            else:
                application.status = 'reviewing'
                messages.info(request, "Application has been moved back to Review stage.")
            application.save()
            
            return redirect('interview_detail', interview_id=interview.id)
    else:
        form = InterviewFeedbackForm(instance=interview)
    
    context = {
        'form': form,
        'interview': interview,
        'title': 'Interview Feedback'
    }
    
    return render(request, 'interview_feedback.html', context)

@login_required
def interviewer_feedback(request, interview_id):
    """Submit feedback for a completed interview (Interviewer only)"""
    # Ensure user is an interviewer
    if request.user.role != 'interviewer':
        messages.error(request, "Access denied. Interviewer access required.")
        return redirect('home')
    
    interview = get_object_or_404(JobInterview, pk=interview_id)
    
    # Check if user is the assigned interviewer
    if interview.interviewer != request.user:
        messages.error(request, "Access denied. You are not assigned to this interview.")
        return redirect('interview_list')
    
    if request.method == 'POST':
        form = InterviewerFeedbackForm(request.POST, instance=interview)
        if form.is_valid():
            interview = form.save(commit=False)
            interview.status = 'completed'  # Automatically mark as completed when feedback is submitted
            interview.save()
            
            # Get the recommendation from the form
            recommendation = form.cleaned_data.get('recommendation')
            
            # Update the application status based on interviewer's recommendation
            application = interview.application
            if recommendation == 'accept':
                application.status = 'offered'
                messages.success(request, "Your feedback has been submitted successfully! The candidate has been recommended for job offer.")
            else:  # reject
                application.status = 'rejected'
                messages.success(request, "Your feedback has been submitted successfully! The candidate has not been recommended for this position.")
            
            application.save()
            
            return redirect('interview_detail', interview_id=interview.id)
    else:
        form = InterviewerFeedbackForm(instance=interview)
    
    context = {
        'form': form,
        'interview': interview,
        'title': 'Interviewer Feedback'
    }
    
    return render(request, 'interviewer_feedback.html', context)

@login_required
def candidate_view_interview(request, application_id):
    """View for candidates to see interview details for their application"""
    # Ensure user is a candidate
    if request.user.role != 'candidate':
        messages.error(request, "Access denied. Only candidates can view their interviews.")
        return redirect('home')
    
    try:
        candidate = Candidate.objects.get(user=request.user)
        # Get the application and ensure it belongs to the current candidate
        application = get_object_or_404(JobApplication, id=application_id, candidate=candidate)
        
        # Get the interview related to this application
        interviews = JobInterview.objects.filter(application=application)
        
        if not interviews.exists():
            # No interviews found
            messages.info(request, "No interview has been scheduled for this application yet.")
            return redirect('my_applications')
        
        # Use the most recent interview
        interview = interviews.order_by('-scheduled_date').first()
        
        # Handle interviewer data
        if not interview.interviewer:
            # Create a placeholder interviewer name if none exists
            interview.interviewer = User(first_name="Not", last_name="Assigned")
        
        # Ensure feedback data is formatted properly
        if not interview.interviewer_feedback:
            interview.interviewer_feedback = "No feedback provided yet."
        
        # Make sure rating is set
        if not interview.interviewer_rating:
            interview.interviewer_rating = 0
        
        # Make sure scheduled date is set
        if not hasattr(interview, 'scheduled_date') or not interview.scheduled_date:
            interview.scheduled_date = timezone.now()
        
        context = {
            'interview': interview,
            'application': application,
        }
        return render(request, 'candidate_interview_view.html', context)
    except Candidate.DoesNotExist:
        messages.error(request, "Candidate profile not found.")
        return redirect('home')
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('my_applications')

@login_required
def job_offer_response(request, application_id):
    """Allow candidates to accept or decline job offers"""
    # Ensure user is a candidate
    if request.user.role != 'candidate':
        messages.error(request, "Access denied. Only candidates can respond to job offers.")
        return redirect('home')
    
    try:
        candidate = Candidate.objects.get(user=request.user)
        application = get_object_or_404(JobApplication, id=application_id, candidate=candidate)
        
        # Ensure the application is in 'offered' status
        if application.status != 'offered':
            messages.error(request, "This application does not have a pending job offer.")
            return redirect('my_applications')
        
        if request.method == 'POST':
            form = JobOfferResponseForm(request.POST)
            if form.is_valid():
                response = form.cleaned_data.get('response')
                comments = form.cleaned_data.get('additional_comments', '')
                
                if response == 'accept':
                    application.status = 'accepted'
                    success_message = "Congratulations! You have accepted the job offer."
                else:  # decline
                    application.status = 'rejected'
                    success_message = "You have declined the job offer. Thank you for your consideration."
                
                # Store the comments in the application notes field
                if comments:
                    application.notes = f"Candidate response: {comments}\n\n{application.notes}"
                
                application.save()
                messages.success(request, success_message)
                return redirect('my_applications')
        else:
            form = JobOfferResponseForm()
        
        context = {
            'form': form,
            'application': application,
            'job': application.job,
        }
        return render(request, 'job_offer_response.html', context)
    
    except Candidate.DoesNotExist:
        messages.error(request, "Candidate profile not found.")
        return redirect('home')

@login_required
def delete_application(request, application_id):
    """Delete a job application (HR Coordinator only)"""
    # Ensure user is an HR Coordinator
    if request.user.role != 'hr_coordinator' and not request.user.is_superuser:
        messages.error(request, "Access denied. HR Coordinator access required.")
        return redirect('home')
    
    application = get_object_or_404(JobApplication, pk=application_id)
    
    # Check if there are interviews associated with this application
    has_interviews = JobInterview.objects.filter(application=application).exists()
    
    if request.method == 'POST':
        if has_interviews and not request.POST.get('confirm_with_interviews'):
            # If there are interviews but the user hasn't confirmed deletion
            messages.error(request, "This application has interviews scheduled. Please confirm deletion.")
            return redirect('delete_application', application_id=application_id)
        
        # Store information for success message
        candidate_name = application.candidate.user.get_full_name() or application.candidate.user.username
        job_title = application.job.title
        
        # Delete the application
        application.delete()
        messages.success(request, f"Application from {candidate_name} for '{job_title}' has been deleted successfully.")
        return redirect('application_list')
    
    context = {
        'application': application,
        'has_interviews': has_interviews
    }
    return render(request, 'delete_application_confirm.html', context)

@login_required
def create_staff(request):
    """Create HR coordinators and interviewers (Admin only)"""
    # Ensure user is an admin/superuser
    if not request.user.is_superuser:
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('home')
    
    if request.method == 'POST':
        form = StaffRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            role = request.POST.get('role')
            if role in [User.HR_COORDINATOR, User.INTERVIEWER]:
                user.role = role
                user.save()
                messages.success(request, f"New {user.get_role_display()} account created for {user.username}!")
                return redirect('staff_list')
            else:
                messages.error(request, "Invalid role selected.")
    else:
        form = StaffRegisterForm()
    
    context = {
        'form': form,
        'title': 'Create Staff Account',
        'roles': [
            (User.HR_COORDINATOR, 'HR Coordinator'),
            (User.INTERVIEWER, 'Interviewer')
        ]
    }
    return render(request, 'create_staff.html', context)

@login_required
def staff_list(request):
    """View all HR coordinators and interviewers (Admin only)"""
    # Ensure user is an admin/superuser
    if not request.user.is_superuser:
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('home')
    
    # Get staff users (HR coordinators and interviewers)
    staff_users = User.objects.filter(
        role__in=[User.HR_COORDINATOR, User.INTERVIEWER]
    ).order_by('role', 'username')
    
    context = {
        'staff_users': staff_users,
        'title': 'Staff Management'
    }
    return render(request, 'staff_list.html', context)