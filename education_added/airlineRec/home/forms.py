from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Candidate, Skill, CandidateSkill, Education
import datetime

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

class SkillSearchForm(forms.Form):
    search_term = forms.CharField(required=False, label="Search for skills")

class CandidateSkillForm(forms.ModelForm):
    PROFICIENCY_CHOICES = CandidateSkill.PROFICIENCY_CHOICES
    
    skill = forms.ModelChoiceField(queryset=Skill.objects.all())
    proficiency = forms.ChoiceField(choices=PROFICIENCY_CHOICES)
    years_experience = forms.IntegerField(min_value=0, max_value=50)
    
    class Meta:
        model = CandidateSkill
        fields = ['skill', 'proficiency', 'years_experience']

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
    
    def clean(self):
        cleaned_data = super().clean()
        is_current = cleaned_data.get('is_current')
        end_date = cleaned_data.get('end_date')
        
        if is_current and end_date:
            cleaned_data['end_date'] = None
        elif not is_current and not end_date:
            self.add_error('end_date', 'Please provide an end date or check "currently studying".')
            
        return cleaned_data 

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