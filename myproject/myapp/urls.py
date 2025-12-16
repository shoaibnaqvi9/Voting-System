from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_page, name='login'),
    path('signup/', views.signup_page, name='signup'),
    path('vote/', views.vote_page, name='vote'),
    path('success/', views.success_page, name='success'),
    path('already-voted/', views.already_voted_page, name='already_voted'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('results/', views.results_page, name='results'),
    path('logout/', views.logout_view, name='logout'),
]