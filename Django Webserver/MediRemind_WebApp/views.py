from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.urls import reverse


from .forms import RegisterForm
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
            return redirect(reverse('profile'))  # Use 'reverse' to get the correct URL
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Security check complete. Log the user in."""
        login(self.request, form.get_user())
        return redirect(self.get_success_url())
    
@login_required
def profile(request):
    return render(request, 'MediRemind_WebApp/profile.html', {'user': request.user})