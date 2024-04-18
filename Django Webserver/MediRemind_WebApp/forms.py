# MediRemind_WebApp/forms.py

from django import forms
from .models import Item
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import MedicationSchedule
from .models import MQTTConfiguration
from .models import ManualInput

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'description']  # Replace these with the actual fields of your Item model

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

class ManualInputForm(forms.Form):
    medication_name = forms.CharField(max_length=100)
    dosage = forms.NumberInput()
    time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'type': 'time'
        }, format='%H:%M')
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date'
        }, format='%Y-%m-%d')
    )
    notes = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = ManualInput
        fields = ['medication_name', 'dosage', 'time', 'date', 'notes']

class MQTTConfigurationForm(forms.ModelForm):
    class Meta:
        model = MQTTConfiguration
        fields = ['broker_address', 'port', 'username', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }


