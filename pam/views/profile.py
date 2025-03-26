# backend/views/profile.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from pam.forms import ProfileForm
from pam.models import Profile

@login_required  # Garante que o usuário esteja logado antes de acessar a página
def profile_view(request):
    user = request.user

    # Verifique se o usuário tem um perfil relacionado (se o modelo profile for usado)
    try:
        profile_obj = user.profile  # Obtém o perfil associado ao usuário
    except Profile.DoesNotExist:
        profile_obj = None  # Caso o perfil não exista

    # Dados para exibir no template
    content = {
        'title': 'profile',
        'heading': f'profile of {user.username}',
        'active_page': 'profile',
        'user': user,  # Informações do usuário logado
        'profile': profile_obj,  # Informações do perfil, caso exista
    }

    return render(request, 'components/profile.html', content)

@login_required
def edit_profile_view(request):
    # Obtém o perfil do usuário logado
    profile = request.User.profile

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redireciona para a página do perfil após salvar
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'components/profile.html', {'form': form})
