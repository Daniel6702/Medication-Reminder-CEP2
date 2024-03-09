# MediRemind_WebApp/forms.py

from django import forms
from .models import Item

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'description']  # Replace these with the actual fields of your Item model
