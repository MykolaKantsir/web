from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='dashboard-home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('proxy/', views.proxy, name='dashboard-proxy'),
    path('about/', views.about, name='dashboard-about'),
    path('machine/<int:machine_id>/', views.machine_detail, name='machine_detail'),
    path('job/<int:job_id>/', views.job_detail, name='job_detail'),
    path('job/finish/<int:job_id>/', views.finish_job, name='finish_job'),
    path('job/unarchive/<int:job_id>/', views.unarchive_job, name='unarchive_job'),
    path('get-job-productivity/<int:pk>/', views.get_job_productivity, name='get_job_productivity'),
    path('cycle_timeline/<int:job_id>/', views.cycle_timeline, name='cycle_timeline'),
    path('next-jobs/', views.next_jobs_view, name='next_jobs'),
    path('check-next-jobs/', views.check_next_jobs, name='check_next_jobs'),
    path('update-monitor-operation/', views.update_monitor_operation, name='update_monitor_operation')
    ]