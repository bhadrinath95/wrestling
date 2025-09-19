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
    path('players/images/', views.player_images, name='player-image'),
    path('players/create/', views.player_create, name='player-create'),
    path('players/<int:pk>/view/', views.player_view, name='player-view'),
    path('players/<int:pk>/edit/', views.player_update, name='player-update'),
    path('players/<int:pk>/delete/', views.player_delete, name='player-delete'),
    path('players/<int:pk>/auction/', views.player_auction, name='player-auction'),

    # Championship
    path('championship/', views.championship_list, name='championship-list'),
    path('championship/create/', views.championship_create, name='championship-create'),
    path('championship/<int:pk>/view/', views.championship_detail, name='championship-view'),
    path('championship/<int:pk>/edit/', views.championship_update, name='championship-update'),
    path('championship/<int:pk>/delete/', views.championship_delete, name='championship-delete'),

    # Rules
    path('rule/', views.rule_list, name='rule-list'),
    path('rule/create/', views.rule_create, name='rule-create'),
    path('rule/<int:pk>/view/', views.rule_view, name='rule-view'),
    path('rule/<int:pk>/edit/', views.rule_update, name='rule-update'),
    path('rule/<int:pk>/delete/', views.rule_delete, name='rule-delete'),
]
