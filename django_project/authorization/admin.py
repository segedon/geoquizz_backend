from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('login', 'password')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('login', 'password1', 'password2'),
        }),
    )
    list_display = ('login', 'is_staff')
    list_filter = ('is_staff', )
    search_fields = ('login', )
    ordering = ('login',)


admin.site.register(User, CustomUserAdmin)