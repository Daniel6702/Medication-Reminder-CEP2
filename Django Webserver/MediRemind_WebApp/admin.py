from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.shortcuts import redirect

def login_as_user(modeladmin, request, queryset):
    user = queryset.first()
    if user:
        request.session['impersonate_id'] = user.id
        return redirect('/profile/home')

class MyUserAdmin(UserAdmin):
    actions = [login_as_user]

admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)
