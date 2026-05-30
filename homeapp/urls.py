from .import views
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('',views.index,name='index'),
    path('login/', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    
    path('signup/', views.user_registration, name='signup'),
    path('user_registration', views.user_registration, name='user_registration'),
     path('admin_dashboard', views.admin_dashboard, name='admin_dashboard'),
     path('user_dashboard', views.user_dashboard, name='user_dashboard'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)