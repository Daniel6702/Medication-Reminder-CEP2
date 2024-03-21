from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from rest_framework.authtoken.models import Token
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import HeucodEventSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .forms import RegisterForm
from .models import Item
from .forms import ItemForm
from django.views.generic.list import ListView
from .models import MedicationSchedule
from .forms import MedicationScheduleForm
from .serializers import MedicationScheduleSerializer
from .models import MQTTConfiguration
from .serializers import MQTTConfigurationSerializer
from .forms import MQTTConfigurationForm


class ProfileViews:
    class HomeView(LoginRequiredMixin, TemplateView):
        template_name = 'profile/home.html'

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context['user'] = self.request.user

            return context
        
    class ConfigurationView(LoginRequiredMixin, TemplateView):
        template_name = 'profile/configuration.html'

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            
            # Getting or creating a token for the user
            token, created = Token.objects.get_or_create(user=self.request.user)
            context['token'] = token

            # Getting or creating the MQTT configuration instance for the user
            mqtt_config, created = MQTTConfiguration.objects.get_or_create(
                user=self.request.user,
                defaults={'port': 1883, 'broker_address': 'http://defaultaddress.com'}  # Default values
            )
            context['mqtt_form'] = MQTTConfigurationForm(instance=mqtt_config)

            return context

        def post(self, request, *args, **kwargs):
            mqtt_config, created = MQTTConfiguration.objects.get_or_create(user=request.user)
            form = MQTTConfigurationForm(request.POST, instance=mqtt_config)

            if form.is_valid():
                form.save()
                # Redirect to a success page or the same configuration page
                return redirect(reverse('configuration')) 

            # If the form is not valid, re-render the page with the existing form data
            return self.render_to_response(self.get_context_data(mqtt_form=form))


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

def home(request):
    return render(request, 'MediRemind_WebApp/home_page.html')

def show_items(request):
    items = Item.objects.all()
    return render(request, 'MediRemind_WebApp/items.html', {'items': items})

def add_item(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/items')  # Redirect to another page after saving
    else:
        form = ItemForm()
    return render(request, 'MediRemind_WebApp/add_item.html', {'form': form})

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
    class HeucodEventAPIView(APIView):
        authentication_classes = [TokenAuthentication]
        permission_classes = [IsAuthenticated]

        def post(self, request):
            serializer = HeucodEventSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
