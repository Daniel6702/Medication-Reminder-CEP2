from django.urls import path
from django.contrib import admin
from . import views
from django.contrib.auth.views import LogoutView
from .views import HeucodEventAPIView

profile_urls = [
    path('profile/home', views.ProfileViews.HomeView.as_view(), name='profile_home'),
    path('profile/medication_schedule', views.ProfileViews.MedicationScheduleView.as_view(), name='medication_schedule'),
    path('profile/configuration', views.ProfileViews.ConfigurationView.as_view(), name='configuration'),
    path('profile/events', views.ProfileViews.EventsView.as_view(), name='events'),
    path('profile/data', views.ProfileViews.DataView.as_view(), name='data'),
    path('profile/settings', views.ProfileViews.SettingsView.as_view(), name='settings'),
]

urlpatterns = profile_urls + [
    path('', views.home, name='home'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('items/', views.show_items, name='show_items'),
    path('add/', views.add_item, name='add_item'),
    path('admin/', admin.site.urls),
    path('register/', views.register, name='register'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('api/heucod-events/', HeucodEventAPIView.as_view(), name='heucod_events'),
]
