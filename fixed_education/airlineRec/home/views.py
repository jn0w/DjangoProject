from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, CandidateSkillForm, SkillSearchForm, EducationForm, CandidateEducationForm
from .models import User, Candidate, Skill, CandidateSkill, Education
from django.contrib.auth import logout

def home(request):
    return render(request, 'index.html')

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
    
    # Get candidate profile
    candidate, created = Candidate.objects.get_or_create(user=request.user)
    
    # Get existing skills
    candidate_skills = CandidateSkill.objects.filter(candidate=candidate)
    
    # Process skill search form
    search_form = SkillSearchForm(request.GET or None)
    skills = Skill.objects.all()
    
    if search_form.is_valid() and search_form.cleaned_data.get('search_term'):
        search_term = search_form.cleaned_data.get('search_term')
        skills = skills.filter(name__icontains=search_term)
    
    # Process form submissions
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
    else:
        skill_form = CandidateSkillForm()
    
    context = {
        'candidate': candidate,
        'candidate_skills': candidate_skills,
        'search_form': search_form,
        'skills': skills,
        'skill_form': skill_form
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