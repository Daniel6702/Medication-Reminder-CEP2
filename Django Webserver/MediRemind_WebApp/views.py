from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.utils import OperationalError

from .models import Item
from .forms import ItemForm

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