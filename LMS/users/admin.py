from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import *

# Register your models here.
admin.site.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff')
    search_fields = ('username', 'email')

admin.site.register(Borrower)
