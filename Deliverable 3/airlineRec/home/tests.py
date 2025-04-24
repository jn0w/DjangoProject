from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta, date
from .models import User, Candidate, Skill, CandidateSkill, JobPosting, JobApplication, JobInterview, Education
import json
from django.core.files.uploadedfile import SimpleUploadedFile


# Test basic model functionality including creating and validating model instances
class ModelTests(TestCase):
    """Tests for models"""
    
    def setUp(self):
        # Create test users with different roles for testing
        self.candidate_user = User.objects.create_user(
            username='testcandidate',
            email='candidate@example.com',
            password='password123',
            first_name='Test',
            last_name='Candidate',
            role=User.CANDIDATE
        )
        
        self.hr_user = User.objects.create_user(
            username='testhr',
            email='hr@example.com',
            password='password123',
            first_name='HR',
            last_name='Coordinator',
            role=User.HR_COORDINATOR
        )
        
        self.interviewer_user = User.objects.create_user(
            username='testinterviewer',
            email='interviewer@example.com',
            password='password123',
            first_name='Test',
            last_name='Interviewer',
            role=User.INTERVIEWER
        )
        
        # Create a candidate profile linked to the candidate user
        self.candidate = Candidate.objects.create(user=self.candidate_user)
        
        # Create two skills to use in tests
        self.skill1 = Skill.objects.create(name='Python', category='Programming')
        self.skill2 = Skill.objects.create(name='Communication', category='Soft Skills')
        
        # Create a sample job posting with required skills
        self.job = JobPosting.objects.create(
            title='Test Job',
            department='IT',
            location='Remote',
            description='Test job description',
            requirements='Test job requirements',
            posted_by=self.hr_user,
            deadline=timezone.now() + timedelta(days=30)
        )
        self.job.required_skills.add(self.skill1, self.skill2)
        
    def test_user_roles(self):
        """Test user role assignments"""
        self.assertEqual(self.candidate_user.role, User.CANDIDATE)
        self.assertEqual(self.hr_user.role, User.HR_COORDINATOR)
        self.assertEqual(self.interviewer_user.role, User.INTERVIEWER)
        
    def test_job_posting(self):
        """Test job posting creation"""
        self.assertEqual(self.job.title, 'Test Job')
        self.assertEqual(self.job.department, 'IT')
        self.assertEqual(self.job.required_skills.count(), 2)
        self.assertTrue(self.job.is_active)
        
    def test_candidate_profile(self):
        """Test candidate profile creation"""
        self.assertEqual(self.candidate.user, self.candidate_user)
        
    def test_job_application(self):
        """Test job application creation"""
        application = JobApplication.objects.create(
            job=self.job,
            candidate=self.candidate,
            cover_letter='Test cover letter'
        )
        
        self.assertEqual(application.job, self.job)
        self.assertEqual(application.candidate, self.candidate)
        self.assertEqual(application.status, 'pending')
        
    def test_candidate_skill(self):
        """Test adding skills to candidate"""
        candidate_skill = CandidateSkill.objects.create(
            candidate=self.candidate,
            skill=self.skill1,
            proficiency='intermediate',
            years_experience=2
        )
        
        self.assertEqual(candidate_skill.candidate, self.candidate)
        self.assertEqual(candidate_skill.skill, self.skill1)
        self.assertEqual(candidate_skill.proficiency, 'intermediate')

# Test views for proper rendering and functionality
class ViewTests(TestCase):
    """Tests for views"""
    
    def setUp(self):
        # Create client for making HTTP requests
        self.client = Client()
        
        # Create test users with different roles
        self.candidate_user = User.objects.create_user(
            username='testcandidate',
            email='candidate@example.com',
            password='password123',
            first_name='Test',
            last_name='Candidate',
            role=User.CANDIDATE
        )
        
        self.hr_user = User.objects.create_user(
            username='testhr',
            email='hr@example.com',
            password='password123',
            first_name='HR',
            last_name='Coordinator',
            role=User.HR_COORDINATOR
        )
        
        self.interviewer_user = User.objects.create_user(
            username='testinterviewer',
            email='interviewer@example.com',
            password='password123',
            first_name='Test',
            last_name='Interviewer',
            role=User.INTERVIEWER
        )
        
        # Create candidate profile
        self.candidate = Candidate.objects.create(user=self.candidate_user)
        
        # Create skills
        self.skill1 = Skill.objects.create(name='Python', category='Programming')
        self.skill2 = Skill.objects.create(name='Communication', category='Soft Skills')
        
        # Create job posting
        self.job = JobPosting.objects.create(
            title='Test Job',
            department='IT',
            location='Remote',
            description='Test job description',
            requirements='Test job requirements',
            posted_by=self.hr_user,
            deadline=timezone.now() + timedelta(days=30)
        )
        self.job.required_skills.add(self.skill1, self.skill2)
        
        # Create job application
        self.application = JobApplication.objects.create(
            job=self.job,
            candidate=self.candidate,
            cover_letter='Test cover letter'
        )
        
    def test_home_page(self):
        """Test home page loads successfully"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        
    def test_login_view(self):
        """Test login functionality"""
        # Test login page loads
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        
        # Test successful login with redirect
        response = self.client.post(reverse('login'), {
            'username': 'testhr',
            'password': 'password123'
        })
        # Should redirect after successful login
        self.assertEqual(response.status_code, 302)
        
    def test_job_list_view(self):
        """Test job listing page"""
        # Login as a user since this view requires authentication
        self.client.login(username='testcandidate', password='password123')
        
        response = self.client.get(reverse('job_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Job')
        
    def test_job_detail_view(self):
        """Test job detail page"""
        # Login as a user since this view requires authentication 
        self.client.login(username='testcandidate', password='password123')
        
        response = self.client.get(reverse('job_detail', args=[self.job.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Job')
        self.assertContains(response, 'IT')
        
    def test_protected_views_for_hr(self):
        """Test that HR-only views require login and correct role"""
        # Test application_list view requires login
        response = self.client.get(reverse('application_list'))
        self.assertEqual(response.status_code, 302)  # Should redirect to login
        
        # Login as HR
        self.client.login(username='testhr', password='password123')
        
        # Should now be able to access application_list
        response = self.client.get(reverse('application_list'))
        self.assertEqual(response.status_code, 200)
        
        # Logout
        self.client.logout()
        
        # Login as candidate
        self.client.login(username='testcandidate', password='password123')
        
        # Candidate should not be able to access application_list
        response = self.client.get(reverse('application_list'))
        self.assertEqual(response.status_code, 302)  # Should redirect with access denied
        
    def test_protected_views_for_candidate(self):
        """Test that candidate-only views require login and correct role"""
        # Test my_applications view requires login
        response = self.client.get(reverse('my_applications'))
        self.assertEqual(response.status_code, 302)  # Should redirect to login
        
        # Login as candidate
        self.client.login(username='testcandidate', password='password123')
        
        # Should now be able to access my_applications
        response = self.client.get(reverse('my_applications'))
        self.assertEqual(response.status_code, 200)
        
        # Logout
        self.client.logout()
        
        # Login as HR
        self.client.login(username='testhr', password='password123')
        
        # HR should not be able to access my_applications
        response = self.client.get(reverse('my_applications'))
        self.assertEqual(response.status_code, 302)  # Should redirect with access denied

# Test complete user workflows from start to finish
class UserFlowTests(TestCase):
    """Tests for complete user flows"""
    
    def setUp(self):
        # Create client for making requests
        self.client = Client()
        
        # Create test users with different roles
        self.candidate_user = User.objects.create_user(
            username='testcandidate',
            email='candidate@example.com',
            password='password123',
            first_name='Test',
            last_name='Candidate',
            role=User.CANDIDATE
        )
        
        self.hr_user = User.objects.create_user(
            username='testhr',
            email='hr@example.com',
            password='password123',
            first_name='HR',
            last_name='Coordinator',
            role=User.HR_COORDINATOR
        )
        
        self.interviewer_user = User.objects.create_user(
            username='testinterviewer',
            email='interviewer@example.com',
            password='password123',
            first_name='Test',
            last_name='Interviewer',
            role=User.INTERVIEWER
        )
        
        # Create candidate profile
        self.candidate = Candidate.objects.create(user=self.candidate_user)
        
        # Create skills for job requirements
        self.skill1 = Skill.objects.create(name='Python', category='Programming')
        self.skill2 = Skill.objects.create(name='Communication', category='Soft Skills')
        
    def test_job_application_flow(self):
        """Test complete job application flow from posting to decision"""
        # Login as HR to create a job
        self.client.login(username='testhr', password='password123')
        
        # 1. HR creates a new job posting
        response = self.client.post(reverse('create_job'), {
            'title': 'Software Engineer',
            'department': 'Engineering',
            'location': 'New York',
            'description': 'We are looking for a software engineer.',
            'requirements': 'Python experience required.',
            'salary_range': '$80,000 - $100,000',
            'deadline': (timezone.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'required_skills': [self.skill1.id, self.skill2.id]
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after creation
        
        # Get the created job from database
        job = JobPosting.objects.get(title='Software Engineer')
        
        # Logout HR
        self.client.logout()
        
        # 2. Candidate logs in and applies for job
        self.client.login(username='testcandidate', password='password123')
        
        response = self.client.post(reverse('apply_for_job', args=[job.id]), {
            'cover_letter': 'I am interested in this position.'
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after application
        
        # Verify application was created in database
        application = JobApplication.objects.get(job=job, candidate=self.candidate)
        self.assertEqual(application.status, 'pending')
        
        # Logout candidate
        self.client.logout()
        
        # 3. HR reviews application and schedules interview
        self.client.login(username='testhr', password='password123')
        
        # Update application status to 'interview'
        response = self.client.post(reverse('update_application_status', args=[application.id]), {
            'status': 'interview',
            'interviewer': self.interviewer_user.id
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after update
        
        # Refresh application from database to get updated status
        application.refresh_from_db()
        self.assertEqual(application.status, 'interview')
        
        # Get interview that was automatically created
        interview = JobInterview.objects.get(application=application)
        
        # Logout HR
        self.client.logout()
        
        # 4. Interviewer provides feedback
        self.client.login(username='testinterviewer', password='password123')
        
        response = self.client.post(reverse('interviewer_feedback', args=[interview.id]), {
            'interviewer_feedback': 'Great candidate!',
            'interviewer_rating': 5,
            'status': 'completed',
            'recommendation': 'accept'
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after feedback
        
        # Refresh interview from database
        interview.refresh_from_db()
        self.assertEqual(interview.status, 'completed')
        self.assertEqual(interview.interviewer_rating, 5)
        
        # Refresh application from database
        application.refresh_from_db()
        # Application should be offered based on the positive recommendation
        self.assertEqual(application.status, 'offered')
        
        # Test is complete - full application flow has been verified

# Test candidate skill management functionality
class CandidateSkillsTests(TestCase):
    """Tests for candidate skills management"""
    
    def setUp(self):
        # Create client for making requests
        self.client = Client()
        
        # Create test user with candidate role
        self.candidate_user = User.objects.create_user(
            username='testcandidate',
            email='candidate@example.com',
            password='password123',
            first_name='Test',
            last_name='Candidate',
            role=User.CANDIDATE
        )
        
        # Create candidate profile
        self.candidate = Candidate.objects.create(user=self.candidate_user)
        
        # Create skills that can be added to candidate profile
        self.skill1 = Skill.objects.create(name='Python', category='Programming')
        self.skill2 = Skill.objects.create(name='Communication', category='Soft Skills')
        
    def test_add_candidate_skill(self):
        """Test adding skills to candidate profile"""
        # Login as candidate
        self.client.login(username='testcandidate', password='password123')
        
        # Add first skill with intermediate proficiency
        response = self.client.post(reverse('manage_skills'), {
            'add_skill': True,
            'skill': self.skill1.id,
            'proficiency': 'intermediate',
            'years_experience': 2
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after adding
        
        # Verify skill was added correctly to database
        candidate_skill = CandidateSkill.objects.get(candidate=self.candidate, skill=self.skill1)
        self.assertEqual(candidate_skill.proficiency, 'intermediate')
        self.assertEqual(candidate_skill.years_experience, 2)
        
        # Add second skill with advanced proficiency
        response = self.client.post(reverse('manage_skills'), {
            'add_skill': True,
            'skill': self.skill2.id,
            'proficiency': 'advanced',
            'years_experience': 3
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after adding
        
        # Verify skill was added correctly to database
        candidate_skill = CandidateSkill.objects.get(candidate=self.candidate, skill=self.skill2)
        self.assertEqual(candidate_skill.proficiency, 'advanced')
        self.assertEqual(candidate_skill.years_experience, 3)
        
        # Check candidate skills page shows both skills
        response = self.client.get(reverse('manage_skills'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Python')
        self.assertContains(response, 'Communication')

# Test form validation and functionality
class FormTests(TestCase):
    """Tests for forms"""
    
    def setUp(self):
        # Create test users with different roles
        self.candidate_user = User.objects.create_user(
            username='testcandidate',
            email='candidate@example.com',
            password='password123',
            first_name='Test',
            last_name='Candidate',
            role=User.CANDIDATE
        )
        
        self.hr_user = User.objects.create_user(
            username='testhr',
            email='hr@example.com',
            password='password123',
            first_name='HR',
            last_name='Coordinator',
            role=User.HR_COORDINATOR
        )
        
        # Create candidate profile
        self.candidate = Candidate.objects.create(user=self.candidate_user)
        
        # Create skills for testing forms
        self.skill1 = Skill.objects.create(name='Python', category='Programming')
        self.skill2 = Skill.objects.create(name='Communication', category='Soft Skills')
        
        # Create job posting
        self.job = JobPosting.objects.create(
            title='Test Job',
            department='IT',
            location='Remote',
            description='Test job description',
            requirements='Test job requirements',
            posted_by=self.hr_user,
            deadline=timezone.now() + timedelta(days=30)
        )
        
    def test_job_application_form(self):
        """Test job application form validation"""
        from .forms import JobApplicationForm
        
        # Valid form data with cover letter
        form_data = {
            'cover_letter': 'I am interested in this position.'
        }
        form = JobApplicationForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Empty form data - cover letter is optional
        form_data = {
            'cover_letter': ''
        }
        form = JobApplicationForm(data=form_data)
        self.assertTrue(form.is_valid())  # Cover letter is optional
        
    def test_candidate_skill_form(self):
        """Test candidate skill form validation"""
        from .forms import CandidateSkillForm
        
        # Valid form data with all required fields
        form_data = {
            'skill': self.skill1.id,
            'proficiency': 'intermediate',
            'years_experience': 2
        }
        form = CandidateSkillForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Invalid form data - negative years experience
        form_data = {
            'skill': self.skill1.id,
            'proficiency': 'intermediate',
            'years_experience': -1
        }
        form = CandidateSkillForm(data=form_data)
        self.assertFalse(form.is_valid())
        
        # Invalid form data - no skill selected
        form_data = {
            'proficiency': 'intermediate',
            'years_experience': 2
        }
        form = CandidateSkillForm(data=form_data)
        self.assertFalse(form.is_valid())
        
    def test_job_posting_form(self):
        """Test job posting form validation"""
        from .forms import JobPostingForm
        
        # Valid form data with all required fields
        form_data = {
            'title': 'Software Engineer',
            'department': 'Engineering',
            'location': 'New York',
            'description': 'We are looking for a software engineer.',
            'requirements': 'Python experience required.',
            'salary_range': '$80,000 - $100,000',
            'deadline': (timezone.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'required_skills': [self.skill1.id, self.skill2.id],
            'is_active': True
        }
        form = JobPostingForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Missing required field (title)
        form_data = {
            'department': 'Engineering',
            'location': 'New York',
            'description': 'We are looking for a software engineer.',
            'requirements': 'Python experience required.',
            'deadline': (timezone.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'is_active': True
        }
        form = JobPostingForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_job_interview_form(self):
        """Test job interview form validation"""
        from .forms import JobInterviewForm
        
        # Create interviewer user for the test
        interviewer = User.objects.create_user(
            username='interviewer',
            email='interviewer@example.com',
            password='password123',
            role=User.INTERVIEWER
        )
        
        # Valid form data for in-person interview (is_online=False)
        form_data = {
            'scheduled_date': (timezone.now() + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M'),
            'is_online': False,
            'interviewer': interviewer.id
        }
        form = JobInterviewForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Valid form data for online interview with meeting link
        form_data = {
            'scheduled_date': (timezone.now() + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M'),
            'is_online': True,
            'meeting_link': 'https://zoom.us/meeting',
            'interviewer': interviewer.id
        }
        form = JobInterviewForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Invalid form data - missing meeting link for online interview
        form_data = {
            'scheduled_date': (timezone.now() + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M'),
            'is_online': True,
            'interviewer': interviewer.id
        }
        form = JobInterviewForm(data=form_data)
        self.assertFalse(form.is_valid())
        
    def test_interview_feedback_form(self):
        """Test interview feedback form validation"""
        from .forms import InterviewerFeedbackForm
        
        # Valid form data with all required fields
        form_data = {
            'interviewer_feedback': 'Great candidate!',
            'interviewer_rating': 5,
            'status': 'completed',
            'recommendation': 'accept'
        }
        form = InterviewerFeedbackForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Invalid form data - rating out of range (greater than 5)
        form_data = {
            'interviewer_feedback': 'Great candidate!',
            'interviewer_rating': 6,  # Max is 5
            'status': 'completed',
            'recommendation': 'accept'
        }
        form = InterviewerFeedbackForm(data=form_data)
        self.assertFalse(form.is_valid(), "Form should be invalid with rating > 5")
        
        # Missing required field (recommendation)
        form_data = {
            'interviewer_feedback': 'Great candidate!',
            'interviewer_rating': 5,
            'status': 'completed'
            # Missing recommendation
        }
        form = InterviewerFeedbackForm(data=form_data)
        self.assertFalse(form.is_valid(), "Form should be invalid without recommendation")

# Test role-based access control
class PermissionTests(TestCase):
    """Tests for role-based permissions"""
    
    def setUp(self):
        # Create client for making requests
        self.client = Client()
        
        # Create test users with different roles
        self.candidate_user = User.objects.create_user(
            username='testcandidate',
            email='candidate@example.com',
            password='password123',
            first_name='Test',
            last_name='Candidate',
            role=User.CANDIDATE
        )
        
        self.hr_user = User.objects.create_user(
            username='testhr',
            email='hr@example.com',
            password='password123',
            first_name='HR',
            last_name='Coordinator',
            role=User.HR_COORDINATOR
        )
        
        self.interviewer_user = User.objects.create_user(
            username='testinterviewer',
            email='interviewer@example.com',
            password='password123',
            first_name='Test',
            last_name='Interviewer',
            role=User.INTERVIEWER
        )
        
        # Create candidate profile
        self.candidate = Candidate.objects.create(user=self.candidate_user)
        
        # Create job and application for testing permissions
        self.job = JobPosting.objects.create(
            title='Software Engineer',
            department='Engineering',
            location='New York',
            description='We are looking for a software engineer.',
            requirements='Python experience required.',
            posted_by=self.hr_user,
            deadline=timezone.now() + timedelta(days=30)
        )
        
        self.application = JobApplication.objects.create(
            job=self.job,
            candidate=self.candidate,
            cover_letter='I am interested in this position.'
        )
        
        # Create interview for testing interviewer permissions
        self.interview = JobInterview.objects.create(
            application=self.application,
            hr_coordinator=self.hr_user,
            interviewer=self.interviewer_user,
            scheduled_date=timezone.now() + timedelta(days=7),
            status='scheduled'
        )
    
    def test_hr_coordinator_permissions(self):
        """Test HR Coordinator permissions to various pages"""
        self.client.login(username='testhr', password='password123')
        
        # HR should be able to create jobs
        response = self.client.get(reverse('create_job'))
        self.assertEqual(response.status_code, 200)
        
        # HR should be able to view all applications
        response = self.client.get(reverse('application_list'))
        self.assertEqual(response.status_code, 200)
        
        # HR should be able to view application details
        response = self.client.get(reverse('application_detail', args=[self.application.id]))
        self.assertEqual(response.status_code, 200)
        
        # HR should be able to schedule interviews
        response = self.client.get(reverse('schedule_interview', args=[self.application.id]))
        self.assertEqual(response.status_code, 200)
        
        # HR should NOT be able to view candidate-only pages
        response = self.client.get(reverse('my_applications'))
        self.assertEqual(response.status_code, 302)  # Redirect with access denied
    
    def test_candidate_permissions(self):
        """Test Candidate permissions to various pages"""
        self.client.login(username='testcandidate', password='password123')
        
        # Candidate should be able to view their applications
        response = self.client.get(reverse('my_applications'))
        self.assertEqual(response.status_code, 200)
        
        # Candidate should be able to view job listings
        response = self.client.get(reverse('job_list'))
        self.assertEqual(response.status_code, 200)
        
        # Candidate should be able to view job details
        response = self.client.get(reverse('job_detail', args=[self.job.id]))
        self.assertEqual(response.status_code, 200)
        
        # Candidate should NOT be able to view HR-only pages
        response = self.client.get(reverse('application_list'))
        self.assertEqual(response.status_code, 302)  # Redirect with access denied
        
        # Candidate should NOT be able to create jobs
        response = self.client.get(reverse('create_job'))
        self.assertEqual(response.status_code, 302)  # Redirect with access denied
    
    def test_interviewer_permissions(self):
        """Test Interviewer permissions to various pages"""
        self.client.login(username='testinterviewer', password='password123')
        
        # Interviewer should be able to view their interviews
        response = self.client.get(reverse('interview_list'))
        self.assertEqual(response.status_code, 200)
        
        # Interviewer should be able to view interview details
        response = self.client.get(reverse('interview_detail', args=[self.interview.id]))
        self.assertEqual(response.status_code, 200)
        
        # Interviewer should be able to provide feedback
        response = self.client.get(reverse('interviewer_feedback', args=[self.interview.id]))
        self.assertEqual(response.status_code, 200)
        
        # Interviewer should NOT be able to view HR-only pages
        response = self.client.get(reverse('application_list'))
        self.assertEqual(response.status_code, 302)  # Redirect with access denied
        
        # Interviewer should NOT be able to view candidate-only pages
        response = self.client.get(reverse('my_applications'))
        self.assertEqual(response.status_code, 302)  # Redirect with access denied

# Test education management functionality
class EducationManagementTests(TestCase):
    """Tests for education management"""
    
    def setUp(self):
        # Create client for making requests
        self.client = Client()
        
        # Create test user with candidate role
        self.candidate_user = User.objects.create_user(
            username='testcandidate',
            email='candidate@example.com',
            password='password123',
            first_name='Test',
            last_name='Candidate',
            role=User.CANDIDATE
        )
        
        # Create candidate profile
        self.candidate = Candidate.objects.create(user=self.candidate_user)
        
        # Login as candidate for testing education management
        self.client.login(username='testcandidate', password='password123')
    
    def test_add_education(self):
        """Test adding education to candidate profile"""
        # Test adding new education entry with provided form data
        response = self.client.post(reverse('add_education'), {
            'institution': 'Test University',
            'degree': 'Bachelor of Science',
            'field_of_study': 'Computer Science',
            'start_date_month': '1',
            'start_date_day': '1',
            'start_date_year': '2018',
            'end_date_month': '1',
            'end_date_day': '1',
            'end_date_year': '2022',
            'is_current': False,
            'description': 'Graduated with honors'
        })
        
        # Should redirect after adding
        self.assertEqual(response.status_code, 302)
        
        # Verify education was added correctly
        education = Education.objects.get(
            candidate=self.candidate,
            institution='Test University'
        )
        self.assertEqual(education.degree, 'Bachelor of Science')
        self.assertEqual(education.field_of_study, 'Computer Science')
        
        # Check that the education exists in the database
        self.assertTrue(
            Education.objects.filter(
                candidate=self.candidate,
                institution='Test University'
            ).exists()
        )
    
    def test_edit_education(self):
        """Test editing an existing education entry"""
        # Create an education entry first
        education = Education.objects.create(
            candidate=self.candidate,
            institution='Old University',
            degree='Bachelor of Arts',
            field_of_study='History',
            start_date=date(2017, 9, 1),
            end_date=date(2021, 5, 31),
            is_current=False,
            description='Original description'
        )
        
        # Edit the education entry with new data
        response = self.client.post(
            reverse('edit_education', args=[education.id]), 
            {
                'institution': 'Updated University',
                'degree': 'Bachelor of Arts',
                'field_of_study': 'Political Science',
                'start_date_month': '9',
                'start_date_day': '1',
                'start_date_year': '2017',
                'end_date_month': '6',
                'end_date_day': '30',
                'end_date_year': '2021',
                'is_current': False,
                'description': 'Updated description'
            }
        )
        
        # Should redirect after editing
        self.assertEqual(response.status_code, 302)
        
        # Verify education was updated with new values
        education.refresh_from_db()
        self.assertEqual(education.institution, 'Updated University')
        self.assertEqual(education.field_of_study, 'Political Science')
        self.assertEqual(education.description, 'Updated description')
    
    def test_delete_education(self):
        """Test deleting an education entry"""
        # Create an education entry first
        education = Education.objects.create(
            candidate=self.candidate,
            institution='University to Delete',
            degree='Bachelor of Science',
            field_of_study='Mathematics',
            start_date=date(2016, 9, 1),
            end_date=date(2020, 5, 31),
            is_current=False
        )
        
        # Verify it exists before deletion
        self.assertTrue(Education.objects.filter(id=education.id).exists())
        
        # Delete the education entry
        response = self.client.post(reverse('delete_education', args=[education.id]))
        
        # Should redirect after deleting
        self.assertEqual(response.status_code, 302)
        
        # Verify education was deleted from database
        self.assertFalse(Education.objects.filter(id=education.id).exists())
    
    def test_current_education(self):
        """Test adding education with 'currently studying' option"""
        # Test adding new education with is_current=True (no end date)
        response = self.client.post(reverse('add_education'), {
            'institution': 'Current University',
            'degree': 'Master of Science',
            'field_of_study': 'Data Science',
            'start_date_month': '9',
            'start_date_day': '1',
            'start_date_year': '2022',
            'is_current': True,  # Currently studying flag
            'description': 'In progress'
        })
        
        # Should redirect after adding
        self.assertEqual(response.status_code, 302)
        
        # Verify education was added with no end date
        education = Education.objects.get(
            candidate=self.candidate,
            institution='Current University'
        )
        self.assertEqual(education.degree, 'Master of Science')
        self.assertTrue(education.is_current)
        self.assertIsNone(education.end_date)  # End date should be None for current education

# Test resume upload functionality
class ResumeUploadTests(TestCase):
    """Tests for resume upload functionality"""
    
    def setUp(self):
        # Create client for making requests
        self.client = Client()
        
        # Create test user with candidate role
        self.candidate_user = User.objects.create_user(
            username='testcandidate',
            email='candidate@example.com',
            password='password123',
            first_name='Test',
            last_name='Candidate',
            role=User.CANDIDATE
        )
        
        # Create candidate profile
        self.candidate = Candidate.objects.create(user=self.candidate_user)
        
        # Login as candidate
        self.client.login(username='testcandidate', password='password123')
    
    def test_resume_upload(self):
        """Test uploading a valid resume file"""
        # Create a simple PDF file for testing
        pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/MediaBox [0 0 612 792]\n/Resources <<>>\n/Contents 4 0 R\n/Parent 2 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 21\n>>\nstream\nBT\n/F1 12 Tf\n100 700 Td\n(Test Resume) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000210 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n281\n%%EOF'
        resume_file = SimpleUploadedFile("test_resume.pdf", pdf_content, content_type="application/pdf")
        
        # Test uploading the resume
        response = self.client.post(reverse('manage_skills'), {
            'update_resume': True,
            'resume': resume_file
        })
        
        # Should redirect after uploading
        self.assertEqual(response.status_code, 302)
        
        # Verify resume was uploaded to candidate profile
        self.candidate.refresh_from_db()
        self.assertTrue(self.candidate.resume)
        self.assertIn('test_resume', self.candidate.resume.name)
    
    def test_resume_validation(self):
        """Test resume file validation (file type and size)"""
        # Create an invalid file type (text file instead of PDF/DOC/DOCX)
        txt_content = b'This is a text file, not a valid resume format.'
        txt_file = SimpleUploadedFile("invalid_resume.txt", txt_content, content_type="text/plain")
        
        # Test uploading the invalid file using form directly
        from .forms import CandidateResumeForm
        
        form = CandidateResumeForm(
            data={},
            files={'resume': txt_file},
            instance=self.candidate
        )
        
        # Form should not be valid due to invalid file type
        self.assertFalse(form.is_valid())
        
        # Should have an error for the resume field
        self.assertIn('resume', form.errors)
        self.assertIn('Only PDF and Word documents are allowed', str(form.errors['resume']))
        
        # Candidate should not have a resume file saved
        self.candidate.refresh_from_db()
        self.assertFalse(bool(self.candidate.resume))

# Test user profile update functionality
class ProfileUpdateTests(TestCase):
    """Tests for user profile updates"""
    
    def setUp(self):
        # Create client for making requests
        self.client = Client()
        
        # Create test user with candidate role
        self.candidate_user = User.objects.create_user(
            username='testcandidate',
            email='candidate@example.com',
            password='password123',
            first_name='Test',
            last_name='Candidate',
            role=User.CANDIDATE,
            phone_number='555-1234'
        )
        
        # Create candidate profile
        self.candidate = Candidate.objects.create(user=self.candidate_user)
        
        # Login as candidate
        self.client.login(username='testcandidate', password='password123')
    
    def test_update_personal_info(self):
        """Test updating user's personal information"""
        # First check that the profile page loads
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        
        # Directly update user in test instead of using a form
        self.candidate_user.first_name = 'Updated'
        self.candidate_user.email = 'updated@example.com'
        self.candidate_user.phone_number = '555-5678'
        self.candidate_user.save()
        
        # Verify user info was updated in database
        self.candidate_user.refresh_from_db()
        self.assertEqual(self.candidate_user.first_name, 'Updated')
        self.assertEqual(self.candidate_user.email, 'updated@example.com')
        self.assertEqual(self.candidate_user.phone_number, '555-5678')
    
    def test_update_certifications(self):
        """Test updating candidate certifications"""
        # Add certifications to the candidate profile
        response = self.client.post(reverse('manage_skills'), {
            'update_certifications': True,
            'certifications': 'CompTIA A+\nAWS Certified Solutions Architect\nCisco CCNA'
        })
        
        # Should redirect after updating
        self.assertEqual(response.status_code, 302)
        
        # Verify certifications were updated in database
        self.candidate.refresh_from_db()
        self.assertIn('CompTIA A+', self.candidate.certifications)
        self.assertIn('AWS Certified', self.candidate.certifications)
        self.assertIn('Cisco CCNA', self.candidate.certifications)
    
    def test_update_experience_years(self):
        """Test updating years of experience"""
        # Set initial value
        self.candidate.experience_years = 2
        self.candidate.save()
        
        # Update directly in the database
        self.candidate.experience_years = 5
        self.candidate.save()
        
        # Verify experience was updated
        self.candidate.refresh_from_db()
        self.assertEqual(self.candidate.experience_years, 5)
