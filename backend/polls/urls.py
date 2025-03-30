from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('player/', views.player, name='player'),
    path('draft_year/', views.draft_year, name='draft_year')

]

