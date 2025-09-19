from django.urls import path
from . import views

urlpatterns = [
    # Single Match
    path('tournament/', views.tournament_list, name='tournament_list'),
    path('tournament/<int:pk>/', views.tournament_detail, name='tournament_detail'),
    path('tournament/create/', views.tournament_create, name='tournament_create'),
    path('tournament/create/league/<int:pk>', views.tournament_create_league, name='tournament_create_league'),
    path('tournament/create/match/<int:pk>', views.tournament_match_setup, name='tournament_match_setup'),
    path('tournament/<int:pk>/update/', views.tournament_update, name='tournament_update'),
    path('tournament/<int:pk>/delete/', views.tournament_delete, name='tournament_delete'),
    path('tournament/main_event', views.upcoming_main_tournament, name='main_event'),
    path('tournament/<int:pk>/complete', views.tournament_complete, name='tournament_complete'),

    path('single/', views.singlematch_list, name='singlematch_list'),
    path('single/<int:pk>/', views.singlematch_detail, name='singlematch_detail'),
    path('single/create/', views.singlematch_create, name='singlematch_create'),
    path('single/complete_all_matches/', views.singlematch_complete_all_matches, name='complete_all_matches'),
    path('single/<int:pk>/update/', views.singlematch_update, name='singlematch_update'),
    path('single/<int:pk>/delete/', views.singlematch_delete, name='singlematch_delete'),
    path('single/<int:pk>/run/', views.singlematch_execute, name='singlematch_run'),
    path('single/<int:pk>/create_notification/', views.create_notification, name='create_notification'),
]
