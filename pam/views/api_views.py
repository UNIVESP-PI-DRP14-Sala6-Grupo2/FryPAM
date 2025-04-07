from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from ..models import CloudAccount

@login_required
def cloud_account_detail(request, pk):
    """
    API para obter detalhes de uma conta na nuvem.
    
    Args:
        request: Objeto HttpRequest do Django
        pk (int): ID da conta na nuvem
        
    Returns:
        JsonResponse: Detalhes da conta na nuvem em formato JSON
    """
    account = get_object_or_404(CloudAccount, pk=pk)
    
    # Verificar se o usuário tem permissão para ver esta conta
    # Em um ambiente real, você pode adicionar verificações de permissão aqui
    
    # Obter o nome do tenant
    tenant_name = account.tenant.name if account.tenant else "N/A"
    
    # Obter o nome do nível de acesso
    access_level_name = account.access_level.access_level if account.access_level else "N/A"
    
    # Obter o display name do provider e environment
    provider_display = dict(CloudAccount.CLOUD_PROVIDER).get(account.provider, account.provider)
    environment_display = dict(CloudAccount.ENVIRONMENT_CHOICE).get(account.environment, account.environment)

    # Obter informações do validador
    validator_name = account.tenant.validator.name if account.tenant.validator else "N/A"
    validator_id = account.tenant.validator.id if account.tenant.validator else None
    validator_email = account.tenant.validator.email if account.tenant.validator else "N/A"
    
    # Retornar os detalhes da conta
    return JsonResponse({
        'id': account.id,
        'account': account.account,
        'tenant_name': tenant_name,
        'provider': account.provider,
        'provider_display': provider_display,
        'environment': account.environment,
        'environment_display': environment_display,
        'cloud_username': account.cloud_username,
        'access_level_id': account.access_level.id if account.access_level else None,
        'access_level_name': access_level_name,
        'validator': validator_name,
        'validator_id': validator_id,
        'validator_email': validator_email,
        'is_active': account.is_active,
    })
