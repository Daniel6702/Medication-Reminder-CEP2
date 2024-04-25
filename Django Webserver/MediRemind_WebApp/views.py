from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.views.generic.list import ListView

#RestAPI
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

#Serializers
from .serializers import HeucodEventSerializer
from .serializers import MedicationScheduleSerializer
from .serializers import MQTTConfigurationSerializer
from .serializers import RoomSerializer
from .serializers import DeviceSerializer
from .serializers import AlertConfigurationSerializer
from .serializers import NotificationSerializer

#Models
from .models import MedicationSchedule
from .models import MQTTConfiguration
from .models import Room
from .models import Device
from .models import AlertConfiguration
from .models import Notification
from .models import ManualInput
from .models import StateConfig

#Forms
from .forms import RegisterForm
from .forms import MQTTConfigurationForm
from .forms import MedicationScheduleForm
from .forms import DeviceForm
from .forms import RoomForm
from .forms import StateConfigForm
from .forms import ManualInputForm

class ProfileViews:
    class HomeView(LoginRequiredMixin, TemplateView):
        template_name = 'profile/home.html'

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context['user'] = self.request.user
            context['notifications'] = Notification.objects.filter(user=self.request.user)
            context['schedules'] = MedicationSchedule.objects.filter(user=self.request.user)

            return context
        
    class ConfigurationView(LoginRequiredMixin, TemplateView):
        template_name = 'profile/configuration.html'

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            
            # Getting or creating a token for the user
            token, created = Token.objects.get_or_create(user=self.request.user)
            context['token'] = token
            context['device_form'] = DeviceForm()
            context['devices'] = Device.objects.filter(user=self.request.user)
            context['room_form'] = RoomForm()
            context['rooms'] = Room.objects.filter(user=self.request.user)

            # Getting or creating the MQTT configuration instance for the user
            mqtt_config, created = MQTTConfiguration.objects.get_or_create(
                user=self.request.user,
                defaults={'port': 1883, 'broker_address': 'http://defaultaddress.com'}  # Default values
            )
            context['mqtt_form'] = MQTTConfigurationForm(instance=mqtt_config)

            # Ensure default StateConfig exists
            if not StateConfig.objects.filter(user=self.request.user).exists():
                self.create_default_state_configs(self.request.user)

            state_name = self.request.GET.get('state', 'IDLE')  # Default to 'IDLE' or use the state passed in GET parameters
            state_config, _ = StateConfig.objects.get_or_create(
                user=self.request.user,
                state_name=state_name,
                defaults={'color_code': '#FFFFFF'}  # Default color code if not exists
            )
            context['state_config_form'] = StateConfigForm(instance=state_config)
            context['current_state'] = state_name
            context['state_names'] = StateConfig.STATE_NAMES
            
            return context

        def create_default_state_configs(self, user):
            default_configs = [
                {'state_name': 'IDLE', 'color_code': '#FFFFFF'},
                {'state_name': 'ACTIVE', 'color_code': '#00FF00'},
                {'state_name': 'MEDICATION_TAKEN', 'color_code': '#0000FF'},
                {'state_name': 'MEDICATION_MISSED', 'color_code': '#FF0000'},
                {'state_name': 'ALERT', 'color_code': '#FFFF00'},
            ]
            
            for config in default_configs:
                StateConfig.objects.create(
                    user=user,
                    state_name=config['state_name'],
                    color_code=config['color_code']
                )

        def post(self, request, *args, **kwargs):
            # Initialize both forms
            mqtt_config, _ = MQTTConfiguration.objects.get_or_create(user=request.user)
            mqtt_form = MQTTConfigurationForm(request.POST or None, instance=mqtt_config)
            device_form = DeviceForm(request.POST or None)
            room_form = RoomForm(request.POST or None)
            state_config_form = StateConfigForm(request.POST, request.FILES, instance=StateConfig.objects.get(user=request.user, state_name=request.POST.get('state_name')))

            # Check if MQTT configuration form is submitted
            if 'mqtt_submit' in request.POST:
                if mqtt_form.is_valid():
                    mqtt_form.save()
                    return redirect(reverse('configuration'))  # Adjust the redirect as needed

            # Check if Device form is submitted
            elif 'device_submit' in request.POST:
                if device_form.is_valid():
                    device = device_form.save(commit=False)
                    device.user = request.user
                    device.save()
                    return redirect(reverse('configuration'))  # Adjust the redirect as needed
                
            # Check if Room form is submitted
            elif 'room_submit' in request.POST:
                if room_form.is_valid():
                    room = room_form.save(commit=False)
                    room.user = request.user
                    room.save()
                    return redirect(reverse('configuration'))  # Adjust the redirect as needed
            elif 'state_config_submit' in request.POST and state_config_form.is_valid():
                state_config_form.save()

            # If neither or forms are valid, re-render the page with existing form data
            context = self.get_context_data(mqtt_form=mqtt_form, device_form=device_form, room_form=room_form)
            return self.render_to_response(context)

    class EventsView(LoginRequiredMixin, TemplateView):
        template_name = 'profile/events.html'

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            user_logs = self.request.user.heucod_events.all()
            context['logs'] = user_logs

            return context

    class MedicationScheduleView(LoginRequiredMixin, ListView):
        model = MedicationSchedule
        context_object_name = 'schedules'
        template_name = 'profile/medication_schedule.html'

        def get_queryset(self):
            return MedicationSchedule.objects.filter(user=self.request.user)

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context['form'] = MedicationScheduleForm()  # Add the form to the context
            return context

        def post(self, request, *args, **kwargs):
            form = MedicationScheduleForm(request.POST)
            if form.is_valid():
                schedule = form.save(commit=False)
                schedule.user = request.user
                schedule.save()
                return redirect(reverse('medication_schedule'))
            return self.get(request, *args, **kwargs)

    class DataView(LoginRequiredMixin, TemplateView):
        template_name = 'profile/data.html'

    class SettingsView(LoginRequiredMixin, TemplateView):
        template_name = 'profile/settings.html'

    class ManualInputView(LoginRequiredMixin, TemplateView):
        model = ManualInput
        context = 'manual_input'
        template_name = 'profile/manual_input.html'

        def get_user_medication(self):
            choices = ManualInput.objects.values_list('medication_name', flat=True).distinct()
            form = ManualInputForm(choices=choices)
            return render('profile/manual_input.html', {'form': form})

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context['form'] = ManualInputForm()  # Add the form to the context
            return context
        
        def post(self, request, *args, **kwargs):
            form = ManualInputForm(request.POST)
            if form.is_valid():
                manual_input = form.save(commit=False)
                manual_input.user = request.user
                manual_input.save()
                return redirect(reverse('manual_input'))
            return self.get(request, *args, **kwargs)


def home(request):
    return render(request, 'MediRemind_WebApp/home_page.html')

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse('profile_home'))  # Corrected the reference here
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Security check complete. Log the user in."""
        login(self.request, form.get_user())
        return redirect(self.get_success_url())
    
class APIViews:
    class NotificationAPIView(APIView):
        authentication_classes = [TokenAuthentication]
        permission_classes = [IsAuthenticated]

        def post(self, request):
            request.data["user"] = request.user.id  # Add logged in user to the request data
            serializer = NotificationSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        def get(self, request):
            notifications = Notification.objects.filter(user=request.user)
            serializer = NotificationSerializer(notifications, many=True)
            return Response(serializer.data)

        def delete(self, request, notification_id):
            try:
                notification = Notification.objects.get(notification_id=notification_id, user=request.user)
            except Notification.DoesNotExist:
                return Response({"message": "Notification not found"}, status=status.HTTP_404_NOT_FOUND)
            notification.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
    
    class RoomAPIView(APIView):
        authentication_classes = [TokenAuthentication]
        permission_classes = [IsAuthenticated]

        def get(self, request):
            rooms = Room.objects.filter(user=request.user)
            serializer = RoomSerializer(rooms, many=True)
            return Response(serializer.data)

        def post(self, request):
            serializer = RoomSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        def delete(self, request, room_id):
            room = Room.objects.get(room_id=room_id)
            room.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
    class DeviceAPIView(APIView):
        authentication_classes = [TokenAuthentication]
        permission_classes = [IsAuthenticated]

        def get(self, request):
            devices = Device.objects.filter(user=request.user)
            serializer = DeviceSerializer(devices, many=True)
            return Response(serializer.data)

        def post(self, request):
            serializer = DeviceSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        def delete(self, request, device_id):
            device = Device.objects.get(device_id=device_id)
            device.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
    class AlertConfigurationAPIView(APIView):
        authentication_classes = [TokenAuthentication]
        permission_classes = [IsAuthenticated]

        def get(self, request):
            configs = AlertConfiguration.objects.filter(user=request.user)
            serializer = AlertConfigurationSerializer(configs, many=True)
            return Response(serializer.data)

        def post(self, request):
            serializer = AlertConfigurationSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        def delete(self, request, config_id):
            config = AlertConfiguration.objects.get(config_id=config_id)
            config.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    class MedicationScheduleAPIView(APIView):
        authentication_classes = [TokenAuthentication]
        permission_classes = [IsAuthenticated]

        def get(self, request):
            schedules = MedicationSchedule.objects.filter(user=request.user)
            serializer = MedicationScheduleSerializer(schedules, many=True)
            return Response(serializer.data)

        def post(self, request):
            serializer = MedicationScheduleSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
        def delete(self, request, schedule_id):
            schedule = MedicationSchedule.objects.get(schedule_id=schedule_id)
            schedule.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
    class HeucodEventAPIView(APIView):
        authentication_classes = [TokenAuthentication]
        permission_classes = [IsAuthenticated]

        def post(self, request):
            serializer = HeucodEventSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    class MQTTConfigurationAPIView(APIView):
        authentication_classes = [TokenAuthentication]
        permission_classes = [IsAuthenticated]

        def get(self, request):
            config, created = MQTTConfiguration.objects.get_or_create(user=request.user)
            serializer = MQTTConfigurationSerializer(config)
            return Response(serializer.data)

        def post(self, request):
            config, created = MQTTConfiguration.objects.get_or_create(user=request.user)
            serializer = MQTTConfigurationSerializer(config, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@require_POST
def delete_schedule(request, schedule_id):
    schedule = MedicationSchedule.objects.get(schedule_id=schedule_id)
    schedule.delete()
    return redirect('/profile/medication_schedule')
