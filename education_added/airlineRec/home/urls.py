from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('skills/', views.manage_skills, name='manage_skills'),
    path('skills/delete/<int:skill_id>/', views.delete_skill, name='delete_skill'),
    path('education/', views.education_list, name='education_list'),
    path('education/add/', views.add_education, name='add_education'),
    path('education/<int:education_id>/edit/', views.edit_education, name='edit_education'),
    path('education/<int:education_id>/delete/', views.delete_education, name='delete_education'),
]