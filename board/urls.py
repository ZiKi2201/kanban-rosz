from django.urls import path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'board'

urlpatterns = [
    path('admin', admin.site.urls),
    path('', views.home, name='home'),
    path('register', views.register_request, name='register'),
    path('login', views.login_request, name='login'),
    path('logout', views.logout_request, name='logout'),
]
