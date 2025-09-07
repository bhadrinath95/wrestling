from django.urls import path
from . import views

urlpatterns = [
    # Bands
    path('bands/', views.band_list, name='band-list'),
    path('bands/create/', views.band_create, name='band-create'),
    path('bands/<int:pk>/view/', views.band_view, name='band-view'),
    path('bands/<int:pk>/edit/', views.band_update, name='band-update'),
    path('bands/<int:pk>/delete/', views.band_delete, name='band-delete'),

    # Players
    path('players/', views.player_list, name='player-list'),
    path('players/create/', views.player_create, name='player-create'),
    path('players/<int:pk>/view/', views.player_view, name='player-view'),
    path('players/<int:pk>/edit/', views.player_update, name='player-update'),
    path('players/<int:pk>/delete/', views.player_delete, name='player-delete'),

]
