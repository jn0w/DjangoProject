from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Candidate, Skill, CandidateSkill, Education, JobPosting, JobApplication, JobInterview
import datetime

# User registration form for candidates
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    phone_number = forms.CharField(required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone_number = self.cleaned_data['phone_number']
        # Always set role to candidate for public registration
        user.role = User.CANDIDATE
        
        if commit:
            user.save()
            # Create a candidate profile
            Candidate.objects.create(user=user)
                
        return user 

# Form for searching skills in the database
class SkillSearchForm(forms.Form):
    search_term = forms.CharField(required=False, label="Search for skills")

# Form for candidates to add skills to their profile
class CandidateSkillForm(forms.ModelForm):
    PROFICIENCY_CHOICES = CandidateSkill.PROFICIENCY_CHOICES
    
    skill = forms.ModelChoiceField(queryset=Skill.objects.all())
    proficiency = forms.ChoiceField(choices=PROFICIENCY_CHOICES)
    years_experience = forms.IntegerField(min_value=0, max_value=50)
    
    class Meta:
        model = CandidateSkill
        fields = ['skill', 'proficiency', 'years_experience']

# Form for adding/editing education history
class EducationForm(forms.ModelForm):
    start_date = forms.DateField(
        widget=forms.SelectDateWidget(years=range(1950, datetime.date.today().year + 1)),
    )
    end_date = forms.DateField(
        widget=forms.SelectDateWidget(years=range(1950, datetime.date.today().year + 5)),
        required=False
    )
    is_current = forms.BooleanField(
        required=False, 
        label="I am currently studying here",
        help_text="Check this if you're still attending this institution"
    )
    
    class Meta:
        model = Education
        fields = ['institution', 'degree', 'field_of_study', 'start_date', 'end_date', 'is_current', 'description']
    
    # Validate that either end date is provided or currently studying is checked
    def clean(self):
        cleaned_data = super().clean()
        is_current = cleaned_data.get('is_current')
        end_date = cleaned_data.get('end_date')
        
        if is_current and end_date:
            cleaned_data['end_date'] = None
        elif not is_current and not end_date:
            self.add_error('end_date', 'Please provide an end date or check "currently studying".')
            
        return cleaned_data 

# Form for candidate education that uses simpler year dropdowns
class CandidateEducationForm(forms.ModelForm):
    current_year = datetime.datetime.now().year
    years = [(year, year) for year in range(1950, current_year + 1)]
    
    education_start_year = forms.ChoiceField(choices=years, required=False)
    education_end_year = forms.ChoiceField(choices=years, required=False)
    education_currently_studying = forms.BooleanField(required=False, label="Currently studying")
    
    class Meta:
        model = Candidate
        fields = [
            'education_institution',
            'education_degree',
            'education_field',
            'education_start_year',
            'education_end_year',
            'education_currently_studying',
            'certifications'
        ]
        labels = {
            'education_institution': 'Institution',
            'education_degree': 'Degree/Course',
            'education_field': 'Field of Study',
            'certifications': 'Certifications & Additional Training (one per line)'
        }
        widgets = {
            'certifications': forms.Textarea(attrs={'rows': 4, 'placeholder': 'e.g. FAA Private Pilot License (2022)\nAircraft Maintenance Certification (2020)'}),
        } 

# Form for creating and editing job postings
class JobPostingForm(forms.ModelForm):
    # Override fields to make them required
    title = forms.CharField(required=True)
    department = forms.CharField(required=True)
    location = forms.CharField(required=True)
    description = forms.CharField(required=True, widget=forms.Textarea(attrs={'rows': 5}))
    requirements = forms.CharField(required=True, widget=forms.Textarea(attrs={'rows': 5}))
    salary_range = forms.CharField(required=True)
    deadline = forms.DateTimeField(required=True, widget=forms.DateInput(attrs={'type': 'date'}))
    required_skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        required=True,
        widget=forms.CheckboxSelectMultiple(),
        error_messages={'required': 'Please select at least one required skill.'}
    )
    
    class Meta:
        model = JobPosting
        fields = ['title', 'department', 'location', 'description', 
                  'requirements', 'salary_range', 'deadline', 'required_skills']

# Form for submitting job applications with cover letter
class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['cover_letter']
        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'rows': 6, 
                'placeholder': 'Explain why you\'re a good fit for this position...'
            }),
        } 

# Form for uploading and updating candidate resume
class CandidateResumeForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['resume']
        widgets = {
            'resume': forms.FileInput(attrs={'class': 'form-control'})
        }
    
    # Validate resume file type and size
    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if resume:
            # Validate file extension
            ext = resume.name.split('.')[-1]
            valid_extensions = ['pdf', 'doc', 'docx']
            if ext.lower() not in valid_extensions:
                raise forms.ValidationError('Only PDF and Word documents are allowed.')
            
            # Validate file size (max 5MB)
            if resume.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Resume size cannot exceed 5MB.')
        return resume

# Form for scheduling job interviews
class JobInterviewForm(forms.ModelForm):
    meeting_link = forms.CharField(required=False)
    interviewer = forms.ModelChoiceField(
        queryset=User.objects.filter(role='interviewer'),
        help_text="Select an interviewer to conduct this interview"
    )
    
    class Meta:
        model = JobInterview
        fields = ['scheduled_date', 'is_online', 'meeting_link', 'interviewer']
        widgets = {
            'scheduled_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    # Validate that online interviews have a meeting link
    def clean(self):
        cleaned_data = super().clean()
        is_online = cleaned_data.get('is_online')
        meeting_link = cleaned_data.get('meeting_link')
        
        if is_online and not meeting_link:
            raise forms.ValidationError("Meeting link is required for online interviews")
        
        return cleaned_data

# Form for HR coordinators to provide interview feedback
class InterviewFeedbackForm(forms.ModelForm):
    class Meta:
        model = JobInterview
        fields = ['feedback', 'rating', 'status']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
        }

# Form for updating application status
class ApplicationStatusForm(forms.ModelForm):
    interviewer = forms.ModelChoiceField(
        queryset=User.objects.filter(role='interviewer'),
        required=False,
        help_text="Assign an interviewer for interview stage"
    )
    
    class Meta:
        model = JobApplication
        fields = ['status']
    
    # Validate that interview stage applications have an assigned interviewer
    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        interviewer = cleaned_data.get('interviewer')
        
        if status == 'interview' and not interviewer:
            raise forms.ValidationError("An interviewer must be assigned for interview stage applications")
        
        return cleaned_data

# Form for interviewers to provide candidate feedback
class InterviewerFeedbackForm(forms.ModelForm):
    RECOMMENDATION_CHOICES = [
        ('accept', 'Accept Candidate'),
        ('reject', 'Reject Candidate')
    ]
    
    recommendation = forms.ChoiceField(choices=RECOMMENDATION_CHOICES, required=True, 
                                      help_text="Indicate whether you recommend accepting or rejecting this candidate")
    interviewer_rating = forms.IntegerField(
        min_value=1, 
        max_value=5,
        widget=forms.NumberInput(attrs={'min': 1, 'max': 5})
    )
    
    class Meta:
        model = JobInterview
        fields = ['interviewer_feedback', 'interviewer_rating', 'status', 'recommendation']
        widgets = {
            'interviewer_rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
        }
        labels = {
            'interviewer_feedback': 'Feedback',
            'interviewer_rating': 'Rating (1-5)',
        }

# Form for candidates to respond to job offers
class JobOfferResponseForm(forms.Form):
    RESPONSE_CHOICES = [
        ('accept', 'Accept Job Offer'),
        ('decline', 'Decline Job Offer')
    ]
    
    response = forms.ChoiceField(choices=RESPONSE_CHOICES, required=True,
                                help_text="Please select whether you would like to accept or decline this job offer")
    
    additional_comments = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        required=False,
        help_text="Optional comments regarding your decision"
    )

# Form for admin to create staff accounts (HR coordinators and interviewers)
class StaffRegisterForm(UserCreationForm):
    """Form for admin to create HR coordinators and interviewers"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    phone_number = forms.CharField(required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'password1', 'password2']
    
    def save(self, commit=True, role=None):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone_number = self.cleaned_data['phone_number']
        
        # Set the role if provided (should be either HR_COORDINATOR or INTERVIEWER)
        if role:
            user.role = role
        
        if commit:
            user.save()
                
        return user