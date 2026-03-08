from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    ordering = ('phone_number',)
    list_display = ('phone_number', 'is_staff', 'is_active')
    search_fields = ('phone_number',)

admin.site.register(User, CustomUserAdmin)
