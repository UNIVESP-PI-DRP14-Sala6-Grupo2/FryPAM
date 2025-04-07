from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q

from ..forms import PasswordRequestForm, PasswordWithdrawForm
from ..models import PasswordRequest, User, CloudAccount

import logging
import random   
import string

logger = logging.getLogger(__name__)


def mock_aws_password_rotation(account_id, username):
    """
    Simula a rotação de senha na AWS
    """
    # Gera uma senha aleatória que simula a nova senha da AWS
    chars = string.ascii_letters + string.digits + "!@#$%^&*()"
    new_password = ''.join(random.choice(chars) for i in range(16))
    
    logger.info(f"Simulando rotação de senha para conta {account_id}, usuário {username}")
    

    # client = boto3.client('iam')
    # response = client.update_login_profile(UserName=username, Password=new_password)
    
    return {
        'status': 'success',
        'message': 'Senha rotacionada com sucesso',
        'password': new_password
    }


@login_required
def password_request_list(request):
    """
    Exibe a lista de solicitações de senha do usuário atual
    

    Args:
        request: Objeto HttpRequest do Django
        
    Returns:
        HttpResponse: Renderiza o template com as listas de solicitações
    """
    user = request.user
    
    # Diferentes listas baseadas no grupo do usuário
    if user.role == 'admin':
        # Administradores podem ver todas as solicitações
        pending_requests = PasswordRequest.objects.filter(status='pending')
        active_requests = PasswordRequest.objects.filter(status='active_window')
        past_requests = PasswordRequest.objects.filter(
            status='expired') | PasswordRequest.objects.filter(
            status='used') | PasswordRequest.objects.filter(
            status='rejected'
        )
    elif user.role == 'validator':
        # Validadores veem solicitações onde são o validador designado
        pending_requests = PasswordRequest.objects.filter(
            validator=user, 
            status='pending'
        )
        active_requests = PasswordRequest.objects.filter(
            validator=user, 
            status='active_window'
        )
        past_requests = PasswordRequest.objects.filter(
            validator=user,
            status='expired') | PasswordRequest.objects.filter(
            validator=user, 
            status='used') | PasswordRequest.objects.filter(
            validator=user, 
            status='rejected'
        )
    else:
        # Usuários normais veem apenas suas próprias solicitações
        pending_requests = PasswordRequest.objects.filter(
            requester=user, 
            status='pending'
        )
        active_requests = PasswordRequest.objects.filter(
            requester=user,
            status='active_window'
        )
        past_requests = PasswordRequest.objects.filter(
            requester=user,
            status='expired') | PasswordRequest.objects.filter(
            requester=user, 
            status='used') | PasswordRequest.objects.filter(
            requester=user, 
            status='rejected') | PasswordRequest.objects.filter(
            requester=user, 
            status='approved'
        )
    
    context = {
        'pending_requests': pending_requests,
        'active_requests': active_requests,
        'past_requests': past_requests,
    }
    
    return render(request, 'password_request/password_request_list.html', context)


@login_required
def password_request_create(request):
    """
    Cria uma nova solicitação de senha.

    Args:
        request: Objeto HttpRequest do Django
        
    Returns:
        HttpResponse: Renderiza o formulário ou redireciona para a lista após criação
    """
    if request.method == 'POST':
        form = PasswordRequestForm(request.POST, user=request.user)
        if form.is_valid():
            password_request = form.save(commit=False)
            password_request.requester = request.user
            password_request.status = 'pending'
            
            # Obter o ID do validador do formulário
            validator_id = request.POST.get('validator_id')
            
            if validator_id:
                try:
                    # Buscar o validador pelo ID
                    validator = User.objects.get(id=validator_id)
                    password_request.validator = validator
                except User.DoesNotExist:
                    messages.error(request, 'Erro: Validador não encontrado. Por favor, tente novamente.')
                    return redirect('password_request_list')
            else:
                # Fallback: usar o validador do tenant da conta
                cloud_account = form.cleaned_data['cloud_account']
                if hasattr(cloud_account, 'tenant') and hasattr(cloud_account.tenant, 'validator'):
                    password_request.validator = cloud_account.tenant.validator
                else:
                    messages.error(request, 'Erro: Não foi possível determinar o validador para esta solicitação.')
                    return redirect('password_request_list')
            
            # Definir a data de início da janela como o momento atual
            # (será atualizada quando a janela for ativada)
            password_request.window_start = timezone.now()
            
            password_request.save()
            messages.success(request, 'Solicitação de senha criada com sucesso. Aguardando aprovação.')
            return redirect('password_request_list')
    else:
        form = PasswordRequestForm(user=request.user)
    
    context = {
        'form': form,
    }
    
    return render(request, 'password_request/password_request_form.html', context)


@login_required
def password_request_detail(request, pk):
    """
    Exibe os detalhes de uma solicitação de senha.

    - Dados da solicitação (solicitante, validador, conta, etc.)
    - Status atual e ações disponíveis
    - Tempo restante para janelas ativas
    
    Args:
        request: Objeto HttpRequest do Django
        pk (int): ID da solicitação de senha
        
    Returns:
        HttpResponse: Renderiza o template com os detalhes da solicitação
    """
    password_request = get_object_or_404(PasswordRequest, pk=pk)
    
    # Verificar se o usuário tem permissão para ver esta solicitação
    if request.user != password_request.requester and \
       request.user != password_request.validator and \
       request.user.role != 'admin':
        return HttpResponseForbidden('Você não tem permissão para ver esta solicitação.')
    
    # Calcula tempo restante para janelas ativas
    time_remaining = None
    if password_request.status == 'active_window':
        end_time = password_request.window_start + timezone.timedelta(hours=password_request.requested_window)
        now = timezone.now()
        
        if now > end_time:
            # A janela expirou, atualizar o status
            password_request.status = 'expired'
            password_request.save()
        else:
            # Calcula o tempo restante
            remaining = end_time - now
            hours, remainder = divmod(remaining.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_remaining = f'{remaining.days}d {hours}h {minutes}m'
    
    context = {
        'password_request': password_request,
        'time_remaining': time_remaining,
    }
    
    return render(request, 'password_request/password_request_detail.html', context)


@login_required
def password_request_approve(request, pk):
    """
    Aprova uma solicitação de senha.
 
    Args:
        request: Objeto HttpRequest do Django
        pk (int): ID da solicitação de senha
        
    Returns:
        HttpResponse: Redireciona para os detalhes da solicitação
    """
    password_request = get_object_or_404(PasswordRequest, pk=pk)
    
    # Verificar se o usuário tem permissão para aprovar esta solicitação
    if request.user != password_request.validator and request.user.role != 'admin':
        return HttpResponseForbidden('Você não tem permissão para aprovar esta solicitação.')
    
    # Verificar se a solicitação está pendente
    if password_request.status != 'pending':
        messages.error(request, 'Esta solicitação não pode ser aprovada.')
        return redirect('password_request_detail', pk=pk)
    
    # Aprovar a solicitação
    password_request.status = 'approved'
    password_request.save()
    
    messages.success(request, 'Solicitação aprovada com sucesso.')
    return redirect('password_request_detail', pk=pk)


@login_required
def password_request_reject(request, pk):
    """
    Rejeita uma solicitação de senha.

    Args:
        request: Objeto HttpRequest do Django
        pk (int): ID da solicitação de senha
        
    Returns:
        HttpResponse: Redireciona para os detalhes da solicitação
    """
    password_request = get_object_or_404(PasswordRequest, pk=pk)
    
    # Verificar se o usuário tem permissão para rejeitar esta solicitação
    if request.user != password_request.validator and request.user.role != 'admin':
        return HttpResponseForbidden('Você não tem permissão para rejeitar esta solicitação.')
    
    # Verificar se a solicitação está pendente
    if password_request.status != 'pending':
        messages.error(request, 'Esta solicitação não pode ser rejeitada.')
        return redirect('password_request_detail', pk=pk)
    
    # Rejeitar a solicitação
    password_request.status = 'rejected'
    password_request.save()
    
    messages.success(request, 'Solicitação rejeitada.')
    return redirect('password_request_detail', pk=pk)


@login_required
def password_request_activate(request, pk):
    """
    Ativa a janela de tempo para uma solicitação aprovada.

    Args:
        request: Objeto HttpRequest do Django
        pk (int): ID da solicitação de senha
        
    Returns:
        HttpResponse: Redireciona para os detalhes da solicitação
    """
    password_request = get_object_or_404(PasswordRequest, pk=pk)
    
    # Verificar se o usuário tem permissão para ativar esta solicitação
    if request.user != password_request.requester and request.user.role != 'admin':
        return HttpResponseForbidden('Você não tem permissão para ativar esta solicitação.')
    
    # Verificar se a solicitação está aprovada
    if password_request.status != 'approved':
        messages.error(request, 'Esta solicitação não pode ser ativada.')
        return redirect('password_request_detail', pk=pk)
    
    # Ativar a janela de tempo
    now = timezone.now()
    password_request.status = 'active_window'
    password_request.window_start = now
    password_request.save()
    
    messages.success(request, f'Janela de acesso ativada por {password_request.requested_window} horas.')
    return redirect('password_request_detail', pk=pk)


@login_required
def password_withdraw(request, pk):
    """
    Permite ao usuário retirar a senha de uma solicitação com janela ativa.    

    Args:
        request: Objeto HttpRequest do Django
        pk (int): ID da solicitação de senha
        
    Returns:
        HttpResponse: Renderiza o formulário de confirmação ou exibe a senha
    """
    password_request = get_object_or_404(PasswordRequest, pk=pk)
    
    # Verificar se o usuário tem permissão para retirar esta senha
    if request.user != password_request.requester and request.user.role != 'admin':
        return HttpResponseForbidden('Você não tem permissão para retirar esta senha.')
    
    # Verificar se a solicitação está com janela ativa
    if password_request.status != 'active_window':
        messages.error(request, 'Você só pode retirar senhas de solicitações com janela ativa.')
        return redirect('password_request_detail', pk=pk)
    
    # Verificar se a senha já foi retirada
    if password_request.is_withdraw:
        messages.error(request, 'Esta senha já foi retirada anteriormente.')
        return redirect('password_request_detail', pk=pk)
    
    # Se o formulário foi enviado, processar a solicitação de retirada
    if request.method == 'POST':
        form = PasswordWithdrawForm(request.POST)
        if form.is_valid():
            # Simular a rotação de senha na AWS
            # Em produção, aqui teríamos o código real para rotacionar a senha na AWS
            # Usar diretamente o iam_account, que já é uma instância de CloudAccount
            cloud_account = password_request.iam_account
            
            # Chamar a função mock de rotação de senha
            result = mock_aws_password_rotation(
                account_id=cloud_account.account, 
                username=cloud_account.cloud_username
            )
            
            if result['status'] == 'success':
                # Marcar a senha como retirada
                password_request.is_withdraw = True
                password_request.status = 'used'
                password_request.save()
                
                # Retornar a senha ao usuário
                context = {
                    'password_request': password_request,
                    'password': result['password'],
                    'cloud_account': cloud_account,
                }
                
                return render(request, 'password_request/password_revealed.html', context)
            else:
                messages.error(request, f'Erro ao rotacionar a senha: {result.get("message", "Erro desconhecido")}')
                return redirect('password_request_detail', pk=pk)
    else:
        form = PasswordWithdrawForm()
    
    context = {
        'password_request': password_request,
        'form': form,
    }
    
    return render(request, 'password_request/password_withdraw.html', context)
