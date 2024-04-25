# MediRemind_WebApp/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import MedicationSchedule
from .models import MQTTConfiguration
from .models import Device
from .models import Room
from .models import ManualInput

class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

class MedicationScheduleForm(forms.ModelForm):
    reminder_time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'type': 'time'
        }, format='%H:%M')
    )
    time_window = forms.IntegerField(min_value=0)
    dosage = forms.CharField(max_length=100)
    instructions = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = MedicationSchedule
        fields = ['medication_name', 'reminder_time', 'time_window', 'dosage', 'instructions']

class ManualInputForm(forms.ModelForm):
    medication_name = forms.CharField(max_length=100)
    dosage = forms.CharField(max_length=100)
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date'
        }, format='%Y-%m-%d')
    )
    time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'type': 'time'
        }, format='%H:%M')
    )
    notes = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = ManualInput
        fields = ['medication_name', 'dosage', 'date', 'time', 'notes']
        exclude = ['date']  # Exclude the non-editable 'date' field

class MQTTConfigurationForm(forms.ModelForm):
    class Meta:
        model = MQTTConfiguration
        fields = ['broker_address', 'port', 'username', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }

class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ['name', 'type', 'zigbee_id', 'status', 'room']

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['name', 'connected_rooms']
        widgets = {
            'connected_rooms': forms.CheckboxSelectMultiple(),
        }
