from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('new_template/', views.new_template, name='new_template'),
    path('measure/', views.measure, name='measure'),
    ]