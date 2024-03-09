from django.urls import path
from django.contrib import admin
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('items/', views.show_items, name='show_items'),
    path('add/', views.add_item, name='add_item'),
    path('admin/', admin.site.urls),
]
