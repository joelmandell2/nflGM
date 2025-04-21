from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('player/', views.player, name='player'),
    path('draft_year/', views.draft_year, name='draft_year'),
    path('player_page', views.player_page, name='player_page'),
    path('prediction', views.get_prediction, name='get_prediction')
]

