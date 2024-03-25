from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='dashboard-home'),
    path('proxy/', views.proxy, name='dashboard-proxy'),
    path('about/', views.about, name='dashboard-about'),
    path('job/<int:job_id>/', views.job_detail, name='job_detail'),
    path('job/finish/<int:job_id>/', views.finish_job, name='finish_job'),
    path('job/unarchive/<int:job_id>/', views.unarchive_job, name='unarchive_job'),
    path('get-job-productivity/<int:pk>/', views.get_job_productivity, name='get_job_productivity'),
    ]