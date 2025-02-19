from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('new_template/', views.new_template, name='new_template'),
    path('measure/', views.measure, name='measure'),
    path("api/create_drawing/", views.create_drawing, name="create_drawing"),
    path("api/create_or_update_dimension/", views.create_or_update_dimension, name="create_or_update_dimension"),
    ]