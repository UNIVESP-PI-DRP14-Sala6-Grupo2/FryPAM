from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, Group
from .models import User, Tenant, IAMAccount, PasswordRequest


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'role', 'is_staff', 'is_superuser')

    fieldsets = (
        (
            None,
            {
                'fields': ('email', 'password')
            }
        ),
        (
            'Permissions',
            {
                'fields':
                    ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
            }
        ),
        (
            'Important dates',
            {
                'fields': ('last_login',)
            }
        ),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)


class TenantAdmin(Tenant):
    model = Tenant
    list_display = ('name','environment', 'aws_account_id', 'description')
    search_fields = ('name', 'description')


admin.site.unregister(Group)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Tenant)
admin.site.register(IAMAccount)
admin.site.register(PasswordRequest)
