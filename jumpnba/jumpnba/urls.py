"""jumpnba URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.redirect_home),
    path('<slug:day>', views.todays_games, name='index'),
    path('team/<int:team_id>', views.team_page, name='team_page'),
    path('elo/elo_standing', views.elo_standing, name='elo_standing'),
    path('elo/elo_compare', views.elo_compare, name='elo_compare'),
    
]
