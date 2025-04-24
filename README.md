# AirlineRec - Airline Recruiting System

Website URL: [https://jakub003.pythonanywhere.com/](https://jakub003.pythonanywhere.com/)

AirlineRec helps airlines hire new staff. HR posts jobs, candidates apply, and interviewers give feedback.

## Features

- Three user types: Candidates, HR Coordinators, and Interviewers
- Post and manage job openings
- Candidate profiles with skills and education
- Track job applications
- Schedule interviews and record feedback
- Mobile-friendly design with Bootstrap 5

## Testing

The app has many tests to make sure everything works correctly.

### What I Test

1. **Models** - Testing the database:

   - User roles
   - Job postings
   - Candidate profiles
   - Applications
   - Interviews

2. **Views** - Testing web pages:

   - Login and home pages
   - Job listings
   - Application pages
   - User access limits

3. **Forms** - Testing data entry:

   - Job applications
   - Skill forms
   - Job posting forms
   - Interview forms

4. **User Flows** - Testing common tasks:

   - HR creating jobs
   - Candidates applying
   - Scheduling interviews
   - Submitting feedback

5. **Permissions** - Testing who can do what:
   - What HR can access
   - What candidates can access
   - What interviewers can access

### Running Tests

To run all tests with Django:

```bash
python manage.py test home
```

Or use my simple test script:

```bash
python run_tests.py
```

This runs all tests and shows the results clearly.

## External Resources

This project uses some external libraries and resources. See `public/sources.txt` for details about:

- Font Awesome icons for the user interface
- Bootstrap for responsive design
