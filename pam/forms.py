# pam/forms.py
from django import forms
from django.utils import timezone
from .models import Profile, PasswordRequest, CloudAccount, CloudAccountAccessType

class ProfileForm(forms.ModelForm):
    """
    Formulário para edição de perfil de usuário.
    Permite atualizar a biografia e avatar do usuário.
    """
    class Meta:
        model = Profile
        fields = ['bio', 'avatar']


class PasswordRequestForm(forms.ModelForm):
    """
    Formulário para criar solicitações de retirada de senha.

    """
    cloud_account = forms.ModelChoiceField(
        queryset=CloudAccount.objects.none(),
        label="Conta na Nuvem",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_cloud_account'}),
        required=True
    )
    
    requested_window = forms.IntegerField(
        label="Janela de Tempo (horas)",
        min_value=1,
        max_value=4,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text="Duração da janela de acesso (1-4 horas)"
    )
    
    justification = forms.CharField(
        label="Justificativa",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=True,
        help_text="Explique por que você precisa acessar esta conta"
    )
    
    class Meta:
        model = PasswordRequest
        fields = ['requested_window']
        widgets = {
            'iam_account': forms.HiddenInput()
        }
    
    def __init__(self, *args, **kwargs):
        """
        Inicializa o formulário e configura o queryset para o campo cloud_account
        com base no usuário atual.
        
        Args:
            user: Usuário atual para filtrar as contas disponíveis
        """
        user = kwargs.pop('user', None)
        super(PasswordRequestForm, self).__init__(*args, **kwargs)
        
        # Filtrar contas de nuvem disponíveis conforme o usuário
        if user:
            # Em um ambiente real, você pode querer filtrar as contas conforme os acessos do usuário
            self.fields['cloud_account'].queryset = CloudAccount.objects.filter(is_active=True)

    def save(self, commit=True):
        """
        Salva o formulário e cria um novo objeto PasswordRequest.

        
        Args:
            commit: Se True, salva o objeto no banco de dados
            
        Returns:
            PasswordRequest: A instância de solicitação de senha criada
        """
        instance = super(PasswordRequestForm, self).save(commit=False)
        
        # Define o iam_account com base na conta selecionada
        cloud_account = self.cleaned_data.get('cloud_account')
        if cloud_account:
            instance.iam_account = cloud_account
        
        # Define o horário de início da janela como o momento atual
        from django.utils import timezone
        instance.window_start = timezone.now()
        
        if commit:
            instance.save()
        return instance


class PasswordWithdrawForm(forms.Form):
    """
    Formulário para confirmação de retirada de senha.
    
 - A senha atual será rotacionada
    - A nova senha será exibida apenas uma vez
    - A ação será registrada para fins de auditoria
    """
    confirmation = forms.BooleanField(
        label="Eu entendo que esta ação rotacionará a senha e a exibirá apenas uma vez",
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )