from django.urls import path
from django.contrib import admin
from . import views
from django.contrib.auth.views import LogoutView

profile_urls = [
    path('profile/home', views.ProfileViews.HomeView.as_view(), name='profile_home'),
    path('profile/medication_schedule', views.ProfileViews.MedicationScheduleView.as_view(), name='medication_schedule'),
    path('profile/configuration', views.ProfileViews.ConfigurationView.as_view(), name='configuration'),
    path('profile/events', views.ProfileViews.EventsView.as_view(), name='events'),
    path('profile/data', views.ProfileViews.DataView.as_view(), name='data'),
    path('profile/settings', views.ProfileViews.SettingsView.as_view(), name='settings'),
    path('profile/manual_input', views.ProfileViews.ManualInputView.as_view(), name='manual_input'),
]

api_urls = [
    path('api/medication-schedule/', views.APIViews.MedicationScheduleAPIView.as_view(), name='medication_schedule_api'),
    path('api/heucod-events/', views.APIViews.HeucodEventAPIView.as_view(), name='heucod_events'),
    path('api/delete_schedule/<uuid:schedule_id>/', views.delete_schedule, name='delete_schedule'),
    path('api/mqtt-configuration/', views.APIViews.MQTTConfigurationAPIView.as_view(), name='mqtt_configuration_api'),
]

urlpatterns =       \
    profile_urls +  \
    api_urls +      \
    [
    path('', views.home, name='home'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('items/', views.show_items, name='show_items'),
    path('add/', views.add_item, name='add_item'),
    path('admin/', admin.site.urls),
    path('register/', views.register, name='register'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout')
    ]
