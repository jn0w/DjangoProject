from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, CandidateSkillForm, SkillSearchForm, EducationForm, CandidateEducationForm, JobPostingForm, JobApplicationForm, CandidateResumeForm
from .models import User, Candidate, Skill, CandidateSkill, Education, JobPosting, JobApplication
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
    
    context = {
        'application': application,
        'candidate_skills': candidate_skills,
        'status_choices': JobApplication._meta.get_field('status').choices
    }
    
    return render(request, 'application_detail.html', context)

@login_required
def update_application_status(request, application_id):
    """Update the status of a job application (HR Coordinator only)"""
    # Ensure user is an HR Coordinator
    if request.user.role != 'hr_coordinator' and not request.user.is_superuser:
        messages.error(request, "Access denied. HR Coordinator access required.")
        return redirect('home')
    
    if request.method == 'POST':
        application = get_object_or_404(JobApplication, pk=application_id)
        new_status = request.POST.get('status')
        
        # Validate the status
        valid_statuses = [choice[0] for choice in JobApplication._meta.get_field('status').choices]
        if new_status in valid_statuses:
            application.status = new_status
            application.save()
            messages.success(request, f"Application status updated to {application.get_status_display()}")
        else:
            messages.error(request, "Invalid status provided")
        
        return redirect('application_detail', application_id=application_id)
    
    # If not POST, redirect to application detail
    return redirect('application_detail', application_id=application_id)

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
            # Mark application as withdrawn
            application.status = 'withdrawn'
            application.save()
            messages.success(request, "Your application has been withdrawn successfully.")
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