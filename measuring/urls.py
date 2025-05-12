from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('new_template/', views.new_template, name='new_template'),

    # Measurement page with optional drawing_id
    path('measure/', views.measure_view, name='measure'),
    path('measure/<int:drawing_id>/', views.measure_view, name='measure_with_drawing'),

    # API endpoints
    path("api/create_drawing/", views.create_drawing, name="create_drawing"),
    path("api/create_or_update_dimension/", views.create_or_update_dimension, name="create_or_update_dimension"),
    path("api/drawing/<int:drawing_id>/", views.get_drawing_data, name="get_drawing_data"),
    path("api/save_measurement/", views.save_measurement, name="save_measurement"),
    path("api/download_protocol/", views.download_protocol, name="download_protocol"),
]