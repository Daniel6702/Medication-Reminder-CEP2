from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.dateformat import DateFormat




#RestAPI
from rest_framework.authtoken.models import Token

#Models
from .models import MedicationSchedule
from .models import MQTTConfiguration
from .models import Room
from .models import Device
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

import json
import uuid

@login_required
def notifications_view(request):
    page_number = int(request.GET.get('page', 1))
    notifications = Notification.objects.filter(user=request.user).order_by('-timestamp')
    paginator = Paginator(notifications, 9)

    try:
        notifications_page = paginator.page(page_number)
    except PageNotAnInteger:
        notifications_page = paginator.page(1)  # Load the first page if the page number is not an integer
    except EmptyPage:
        notifications_page = paginator.page(paginator.num_pages)  # Load the last page if the page is out of range

    notifications_data = [{
        'message': notification.message,
        'timestamp': DateFormat(notification.timestamp).format('M d, Y H:i'),  # Formatting here
        'type': notification.type
    } for notification in notifications_page.object_list]

    return JsonResponse({
        'notifications': notifications_data,
        'has_next': notifications_page.has_next(),
        'has_prev': notifications_page.has_previous()
    })


class ProfileViews:
    class HomeView(LoginRequiredMixin, TemplateView):
        template_name = 'profile/home.html'

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context['user'] = self.request.user
            context['notifications'] = Notification.objects.filter(user=self.request.user)
            context['schedules'] = MedicationSchedule.objects.filter(user=self.request.user)

            return context
        
    class DashView(LoginRequiredMixin, TemplateView):
        template_name = 'profile/dashboard.html'

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context['user'] = self.request.user
            context['notifications'] = Notification.objects.filter(user=self.request.user)
            context['schedules'] = MedicationSchedule.objects.filter(user=self.request.user)

            return context
        
       
    class EventsView(LoginRequiredMixin, TemplateView):
        template_name = 'profile/events.html'

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            user_logs = self.request.user.heucod_events.all()
            context['logs'] = user_logs

            return context
        
    class AnalysisView(LoginRequiredMixin, TemplateView):
        template_name = 'profile/analysis.html'

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context['user'] = self.request.user
            context['notifications'] = Notification.objects.filter(user=self.request.user)
            context['schedules'] = MedicationSchedule.objects.filter(user=self.request.user)

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

    
    class CustomUserChangeForm(UserChangeForm):
        class Meta:
            model = User
            fields = ['username', 'email', 'first_name', 'last_name']

    class CustomPasswordChangeForm(PasswordChangeForm):
        pass

    class SettingsView(LoginRequiredMixin, TemplateView):
        template_name = 'profile/settings.html'

    class ManualInputView(LoginRequiredMixin, TemplateView):
        model = ManualInput
        context = 'manual_input'
        template_name = 'profile/manual_input.html'

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

@require_POST
def delete_schedule(request, schedule_id):
    schedule = MedicationSchedule.objects.get(schedule_id=schedule_id)
    schedule.delete()
    return redirect('/profile/medication_schedule')
