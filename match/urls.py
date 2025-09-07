from django.urls import path
from . import views

urlpatterns = [
    # Single Match
    path('single/', views.singlematch_list, name='singlematch_list'),
    path('single/<int:pk>/', views.singlematch_detail, name='singlematch_detail'),
    path('single/create/', views.singlematch_create, name='singlematch_create'),
    path('single/<int:pk>/update/', views.singlematch_update, name='singlematch_update'),
    path('single/<int:pk>/delete/', views.singlematch_delete, name='singlematch_delete'),
    path('single/<int:pk>/run/', views.singlematch_execute, name='singlematch_run'),
    path('single/<int:pk>/create_notification/', views.create_notification, name='create_notification'),
]
