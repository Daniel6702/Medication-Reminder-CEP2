from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from rest_framework.authtoken.models import Token
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import HeucodEventSerializer
from .models import HeucodEvent 
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


from .forms import RegisterForm
from .models import Item
from .forms import ItemForm

class ProfileView():

    @staticmethod
    @login_required
    def HomeView(request):
        return render(request, 'profile/home.html')

    @staticmethod
    @login_required
    def MedicationScheduleView(request):
        return render(request, 'profile/medication_schedule.html')
    
    @staticmethod
    @login_required
    def ConfigurationView(request):
        token, created = Token.objects.get_or_create(user=request.user)
        context = {
            'token': token,
        }
        return render(request, 'profile/configuration.html')
    
    @staticmethod
    @login_required
    def EventsView(request):
        return render(request, 'profile/events.html')
    
    @staticmethod
    @login_required
    def DataView(request):
        return render(request, 'profile/data.html')

    @staticmethod
    @login_required
    def SettingsView(request):
        return render(request, 'profile/settings.html')
    
    
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
            token, created = Token.objects.get_or_create(user=self.request.user)
            context['token'] = token

            return context

    class EventsView(LoginRequiredMixin, TemplateView):
        template_name = 'profile/events.html'

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            user_logs = self.request.user.heucod_events.all()
            context['logs'] = user_logs

            return context

    class MedicationScheduleView(LoginRequiredMixin, TemplateView):
        template_name = 'profile/medication_schedule.html'

    class DataView(LoginRequiredMixin, TemplateView):
        template_name = 'profile/data.html'

    class SettingsView(LoginRequiredMixin, TemplateView):
        template_name = 'profile/settings.html'


@login_required
def profile(request):
    token, created = Token.objects.get_or_create(user=request.user)
    user_logs = request.user.heucod_events.all()  
    print("User logs:", user_logs)  

    context = {
        'user': request.user,
        'token': token,
        'logs': user_logs,  
    }
    return render(request, 'base_profile.html', context)


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

def index(request):
    return render(request, 'index.html')

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
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
    

class HeucodEventAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print("Received data:", request.data)
        serializer = HeucodEventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
