from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, Group
from django.utils import timezone
from django.db.models import Count
from django.template.response import TemplateResponse
from django.urls import path

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
            'fields': ('name','validator' ,'is_active'),
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'validator', 'is_active'),
        }),
    )

    list_display = ('name', 'validator','is_active')
    search_fields = ('name','validator__name')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'validator':
            kwargs['queryset'] = User.objects.filter(role__in=['admin', 'validator'])
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class CustomCloudAccountAdmin(admin.ModelAdmin):
    list_display = ('account', 'tenant', 'provider', 'environment', 'cloud_username', 'access_level', 'is_active')
    search_fields = ('account', 'tenant__name', 'cloud_username', 'is_active' )

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
                'fields': ('account', 'tenant', 'provider', 'environment', 'cloud_username', 'access_level', 'is_active')
             }
         ),
    )

class CustomPasswordRequestAdmin(admin.ModelAdmin):
    # Campos exibidos na listagem de requisições de senha
    list_display = ('requester', 'get_account_info', 'validator', 'status', 'requested_window', 
                   'window_start', 'is_withdraw', 'created_at', 'time_remaining', 'actions_column')
    
    # Filtros disponíveis na interface de administração
    list_filter = ('status', 'is_withdraw', 'requested_window', 'created_at')
    
    # Campos pesquisáveis na interface de administração
    search_fields = ('requester__name', 'requester__email', 'validator__name', 'validator__email', 'iam_account__access_level')
    
    # Campos somente leitura que não podem ser editados
    readonly_fields = ('created_at',)
    
    # Hierarquia de datas para navegação temporal
    date_hierarchy = 'created_at'
    
    # Ações em lote disponíveis para o administrador
    actions = ['approve_requests', 'reject_requests', 'mark_as_expired', 'activate_window']
    
    # Template personalizado para a lista de requisições
    change_list_template = 'admin/password_request_change_list.html'
    
    def get_urls(self):
        # Adiciona URLs personalizadas para o dashboard
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_site.admin_view(self.dashboard_view), name='password_request_dashboard'),
        ]
        return custom_urls + urls
    
    def changelist_view(self, request, extra_context=None):
        # Adiciona dados do dashboard à visualização da lista
        extra_context = extra_context or {}
        
        # Obtém contagem para cada status
        status_counts = PasswordRequest.objects.values('status').annotate(count=Count('status'))
        status_data = {item['status']: item['count'] for item in status_counts}
        
        # Obtém janelas ativas que expirarão em breve (nas próximas 24 horas)
        now = timezone.now()
        expiring_soon = PasswordRequest.objects.filter(
            status='active_window',
            window_start__lte=now - timezone.timedelta(hours=1) + timezone.timedelta(hours=4)  # Janela - 1 hora restante
        ).count()
        
        # Obtém requisições recentes (últimas 24 horas)
        recent_requests = PasswordRequest.objects.filter(
            created_at__gte=now - timezone.timedelta(days=1)
        ).count()
        
        # Atualiza o contexto com os dados estatísticos
        extra_context.update({
            'pending_count': status_data.get('pending', 0),
            'active_count': status_data.get('active_window', 0),
            'approved_count': status_data.get('approved', 0),
            'rejected_count': status_data.get('rejected', 0),
            'expired_count': status_data.get('expired', 0),
            'used_count': status_data.get('used', 0),
            'expiring_soon': expiring_soon,
            'recent_requests': recent_requests,
        })
        
        return super().changelist_view(request, extra_context=extra_context)
    
    # URL personalizada para o dashboard
    def dashboard_view(self, request):
        # Visualização detalhada do dashboard
        context = {
            'title': 'Password Request Dashboard',
            # Adicione estatísticas mais detalhadas aqui
        }
        return TemplateResponse(request, 'admin/password_request_dashboard.html', context)
    
    # Configuração dos campos no formulário de edição
    fieldsets = (
        ('Request Information', {
            'fields': ('requester', 'iam_account', 'validator', 'status')
        }),
        ('Time Window', {
            'fields': ('requested_window', 'window_start', 'is_withdraw')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )
    
    def get_account_info(self, obj):
        """Exibe informações da conta em um formato mais legível"""
        return f"{obj.iam_account.access_level}"
    
    get_account_info.short_description = 'Account Access Type'
    
    def time_remaining(self, obj):
        """Calcula e exibe o tempo restante para janelas ativas"""
        if obj.status != 'active_window':
            return '-'
        
        # Calcula o horário de término com base no início da janela e duração solicitada (em horas)
        end_time = obj.window_start + timezone.timedelta(hours=obj.requested_window)
        now = timezone.now()
        
        if now > end_time:
            return 'Expired'
        
        # Calcula o tempo restante
        remaining = end_time - now
        hours, remainder = divmod(remaining.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        return f'{remaining.days}d {hours}h {minutes}m'
    
    time_remaining.short_description = 'Time Remaining'
    
    def actions_column(self, obj):
        """Exibe botões de ação com base no status atual"""
        if obj.status == 'pending':
            return 'Pending Approval'
        elif obj.status == 'active_window':
            return 'Active'
        elif obj.status == 'expired':
            return 'Expired'
        elif obj.status == 'approved':
            return 'Approved'
        elif obj.status == 'rejected':
            return 'Rejected'
        elif obj.status == 'used':
            return 'Used'
        return obj.status
    
    actions_column.short_description = 'Status Info'
    
    def approve_requests(self, request, queryset):
        """Aprova em lote requisições de senha pendentes"""
        updated = queryset.filter(status='pending').update(status='approved')
        self.message_user(request, f'{updated} password requests were approved successfully.')
    
    approve_requests.short_description = "Approve selected password requests"
    
    def reject_requests(self, request, queryset):
        """Rejeita em lote requisições de senha pendentes"""
        updated = queryset.filter(status='pending').update(status='rejected')
        self.message_user(request, f'{updated} password requests were rejected.')
    
    reject_requests.short_description = "Reject selected password requests"
    
    def mark_as_expired(self, request, queryset):
        """Marca requisições com janela ativa como expiradas"""
        updated = queryset.filter(status='active_window').update(status='expired')
        self.message_user(request, f'{updated} password requests were marked as expired.')
    
    mark_as_expired.short_description = "Mark selected requests as expired"
    
    def activate_window(self, request, queryset):
        """Ativa a janela de tempo para requisições aprovadas"""
        now = timezone.now()
        # Ativa apenas requisições aprovadas
        updated = queryset.filter(status='approved').update(
            status='active_window',
            window_start=now
        )
        self.message_user(request, f'{updated} password requests were activated with time window starting now.')
    
    activate_window.short_description = "Activate time window for selected requests"

# Tabelas que vao aparecer no admin
# admin.site.register(model, classe_customizada)

admin.site.register(User, CustomUserAdmin)
admin.site.register(Tenant,CustomTenantAdmin)
admin.site.register(CloudAccountAccessType)
admin.site.register(CloudAccount, CustomCloudAccountAdmin)
admin.site.register(PasswordRequest, CustomPasswordRequestAdmin)

#remover a tabela grupos do admin
admin.site.unregister(Group)
