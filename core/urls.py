from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('upload/', views.upload_statement, name='upload'),
    path('categories/', views.manage_categories, name='manage_categories'),
    path('transaction/<int:transaction_id>/edit/', views.edit_transaction, name='edit_transaction'),
]