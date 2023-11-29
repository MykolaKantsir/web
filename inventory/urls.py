from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search_product/', views.search_product, name='search_product'),
    path('search_category/', views.search_category, name='search_category'),
    path('create_order/', views.create_order, name='create_order'),
    path('orders/', views.orders_page, name='orders_page'),
    path('change_order_status/<int:order_id>/', views.change_order_status, name='change_order_status'),
    path('delete_order/<int:order_id>/', views.delete_order, name='delete_order'),
    path('add_product/', views.add_product_selection, name='add_product_selection'),
    path('add_product/<str:product_type>/', views.add_product, name='add_product'),
    path('add_comment/<int:order_id>/', views.add_comment, name='add_comment'),
    path('scanner/', views.scanner, name='scanner'),
    # Add more app-specific URLs here
]
