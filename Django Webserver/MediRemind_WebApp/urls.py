from django.urls import path
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from .views import ProfileViews, delete_schedule, home, CustomLoginView, register
from .Views.room_views import delete_room, add_room, update_room_position, connect_rooms 
from .Views.api_views import MedicationScheduleAPIView, HeucodEventAPIView, MQTTConfigurationAPIView, RoomAPIView, DeviceAPIView, NotificationAPIView, StateConfigAPIView, EventAPIView
from .Views.configuration_view import ConfigurationView

profile_urls = [
    path('profile/home', ProfileViews.HomeView.as_view(), name='profile_home'),
    path('profile/medication_schedule', ProfileViews.MedicationScheduleView.as_view(), name='medication_schedule'),
    path('profile/configuration', ConfigurationView.as_view(), name='configuration'),
    path('profile/events', ProfileViews.EventsView.as_view(), name='events'),
    path('profile/data', ProfileViews.DataView.as_view(), name='data'),
    path('profile/settings', ProfileViews.SettingsView.as_view(), name='settings'),
    path('profile/manual_input', ProfileViews.ManualInputView.as_view(), name='manual_input'),
    path('profile/dashboard.html', ProfileViews.DashView.as_view(), name='dashboard'),
]

api_urls = [
    path('api/medication-schedule/', MedicationScheduleAPIView.as_view(), name='medication_schedule_api'),
    path('api/heucod-events/', HeucodEventAPIView.as_view(), name='heucod_events'),
    path('api/delete_schedule/<uuid:schedule_id>/', delete_schedule, name='delete_schedule'),
    path('api/mqtt-configuration/', MQTTConfigurationAPIView.as_view(), name='mqtt_configuration_api'),
    path('api/room/', RoomAPIView.as_view(), name='room_api'),
    path('api/device/', DeviceAPIView.as_view(), name='device_api'),
    path('api/notification/', NotificationAPIView.as_view(), name='notification_api'),
    path('api/state_config/', StateConfigAPIView.as_view(), name='state_config_api'),
    path('api/event/', EventAPIView.as_view(), name='event_api'),
]

urlpatterns = profile_urls + api_urls + \
    [
    path('', home, name='home'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('admin/', admin.site.urls),
    path('register/', register, name='register'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('profile/connect_rooms/', connect_rooms, name='connect_rooms'),
    path('profile/add_room/', add_room, name='add_room'),
    path('profile/delete_room/', delete_room, name='delete_room'),
    path('profile/update_room_position/', update_room_position, name='update_room_position'),
] 
