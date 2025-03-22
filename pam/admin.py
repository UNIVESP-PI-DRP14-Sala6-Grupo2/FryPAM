from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, Group

from .models import User, Tenant, PasswordRequest, CloudAccount, CloudAccountAccessType


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'name', 'role', 'is_staff', 'is_superuser')

    fieldsets = (
        (
            None,
            {
                'fields': ('email','name')
            }
        ),
        (
            'Password',
            {
                'fields': ('password',)
            }
        ),
        (
            'Permissions',
            {
                'fields':
                    ('role', 'is_active', 'is_staff', 'is_superuser',)
            }
        ),
        (
            'Other Information',
            {
                'fields': ('last_login','observation')
            }
        ),
    )

    #adiciono um novo registro
    add_fieldsets = [
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'email', 'password1', 'password2'),
        }
    ),
    ('Permissions',
        {
            'fields':
                ('role', 'is_active', 'is_staff', 'is_superuser',)
        }
    ),
    ('Other Information', {
                'fields': ('observation',)
            }
        ),
    ]

    search_fields = ('email','name')
    ordering = ('email','name')

class CustomTenantAdmin(admin.ModelAdmin):

    fieldsets = (
        (None, {
            'fields': ('name','validator' ,'status'),
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'validator', 'status'),
        }),
    )

    list_display = ('name', 'validator','status')
    search_fields = ('name','validator__name')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'validator':
            kwargs['queryset'] = User.objects.filter(role__in=['admin', 'validator'])
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class CustomCloudAccountAdmin(admin.ModelAdmin):
    list_display = ('account', 'tenant', 'provider', 'environment', 'cloud_username', 'access_level', 'status')
    search_fields = ('account', 'tenant__name', 'cloud_username', 'status' )

    add_fieldsets = (
        (None,
            {
                'classes': ('wide',),
                'fields': ('account', 'tenant', 'provider', 'environment', 'cloud_username', 'access_level')
            }
         ),
    )
    fieldsets = (
        (None,
             {
                'fields': ('account', 'tenant', 'provider', 'environment', 'cloud_username', 'access_level', 'status')
             }
         ),
    )

# Tabelas que vao aparecer no admin
# admin.site.register(model, classe_customizada)

admin.site.register(User, CustomUserAdmin)
admin.site.register(Tenant,CustomTenantAdmin)
admin.site.register(CloudAccountAccessType)
admin.site.register(CloudAccount, CustomCloudAccountAdmin)
admin.site.register(PasswordRequest)

#remover a tabela grupos do admin
admin.site.unregister(Group)
