from django.urls import path
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from .views import ProfileViews, APIViews, delete_schedule, home, CustomLoginView, register

profile_urls = [
    path('profile/home', ProfileViews.HomeView.as_view(), name='profile_home'),
    path('profile/medication_schedule', ProfileViews.MedicationScheduleView.as_view(), name='medication_schedule'),
    path('profile/configuration', ProfileViews.ConfigurationView.as_view(), name='configuration'),
    path('profile/events', ProfileViews.EventsView.as_view(), name='events'),
    path('profile/data', ProfileViews.DataView.as_view(), name='data'),
    path('profile/settings', ProfileViews.SettingsView.as_view(), name='settings'),
    path('profile/manual_input', ProfileViews.ManualInputView.as_view(), name='manual_input'),
    path('profile/dashboard.html', ProfileViews.DashView.as_view(), name='dashboard'),
]

api_urls = [
    path('api/medication-schedule/', APIViews.MedicationScheduleAPIView.as_view(), name='medication_schedule_api'),
    path('api/heucod-events/', APIViews.HeucodEventAPIView.as_view(), name='heucod_events'),
    path('api/delete_schedule/<uuid:schedule_id>/', delete_schedule, name='delete_schedule'),
    path('api/mqtt-configuration/', APIViews.MQTTConfigurationAPIView.as_view(), name='mqtt_configuration_api'),
    path('api/room/', APIViews.RoomAPIView.as_view(), name='room_api'),
    path('api/device/', APIViews.DeviceAPIView.as_view(), name='device_api'),
    path('api/alert-configuration/', APIViews.AlertConfigurationAPIView.as_view(), name='alert_configuration_api'),
    path('api/notification/', APIViews.NotificationAPIView.as_view(), name='notification_api'),
]

urlpatterns = profile_urls + api_urls + \
    [
    path('', home, name='home'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('admin/', admin.site.urls),
    path('register/', register, name='register'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
]
