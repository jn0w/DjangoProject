# AirlineRec - Airline Recruiting System

Website URL: [https://jakub003.pythonanywhere.com/](https://jakub003.pythonanywhere.com/)

AirlineRec is a comprehensive recruiting platform for airlines, allowing HR coordinators to post jobs, candidates to apply, and interviewers to conduct interviews and provide feedback.

## Features

- User roles: Candidates, HR Coordinators, and Interviewers
- Job posting and management
- Candidate profiles with skills and education
- Application tracking system
- Interview scheduling and feedback
- Responsive design with Bootstrap 5

## Testing

The application includes comprehensive automated tests covering models, views, forms, and user flows. Testing uses Django's built-in testing framework.

### Test Coverage

1. **Model Tests** - Testing database models and their relationships:

   - User roles and permissions
   - Job posting creation and relationships
   - Candidate profile and skills
   - Application status tracking
   - Interview scheduling and feedback

2. **View Tests** - Testing HTTP responses and template rendering:

   - Home page and authentication views
   - Job listing and details pages
   - Application management
   - Access control for protected views

3. **Form Tests** - Testing form validation:

   - Job application forms
   - Candidate skill forms
   - Job posting forms
   - Interview scheduling and feedback forms

4. **User Flow Tests** - Testing complete user journeys:

   - Job posting creation by HR
   - Application submission by candidates
   - Interview scheduling and execution
   - Feedback submission by interviewers

5. **Permission Tests** - Testing role-based access control:
   - HR coordinator permissions
   - Candidate permissions
   - Interviewer permissions

### Running Tests

To run all tests:

```bash
python manage.py test home
```

To run specific test classes:

```bash
python manage.py test home.tests.ModelTests
python manage.py test home.tests.ViewTests
python manage.py test home.tests.FormTests
python manage.py test home.tests.UserFlowTests
python manage.py test home.tests.PermissionTests
```

Alternatively, use the provided test runner script:

```bash
python run_tests.py
```

You can also run specific test classes with the runner:

```bash
python run_tests.py home.tests.ModelTests
```

## Test-Driven Development

The application was developed following test-driven development principles:

1. Write tests first to define expected behavior
2. Implement features to pass the tests
3. Refactor code while maintaining test coverage

This approach ensures that all features are thoroughly tested and function as expected across different user roles and scenarios.
