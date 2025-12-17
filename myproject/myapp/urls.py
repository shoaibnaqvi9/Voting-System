from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_page, name='login'),
    path('signup/', views.signup_page, name='signup'),
    path('student/vote/', views.vote_page, name='vote'),
    path('student/success/', views.success_page, name='success'),
    path('student/already-voted/', views.already_voted_page, name='already_voted'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/manage_election/', views.manage_election, name='manage_election'),
    path('admin-dashboard/results/', views.results_page, name='results'),
    path('logout/', views.logout_view, name='logout'),
]