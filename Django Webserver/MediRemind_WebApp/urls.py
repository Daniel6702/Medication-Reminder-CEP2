from django.urls import path
from django.contrib import admin
from . import views
from django.contrib.auth.views import LogoutView
from .views import HeucodEventAPIView


urlpatterns = [
    path('', views.home, name='home'),
    path('accounts/profile/', views.profile, name='profile'),
    path('items/', views.show_items, name='show_items'),
    path('add/', views.add_item, name='add_item'),
    path('admin/', admin.site.urls),
    path('register/', views.register, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('api/heucod-events/', HeucodEventAPIView.as_view(), name='heucod_events'),
]
