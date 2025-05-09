from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            username=email,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "admin")

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser, PermissionsMixin):

    ROLE_CHOICE = [
        ('admin', 'Admin'),
        ('user', 'User'),
        ('validator', 'Validator'),
    ]

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICE, default='user')
    username = models.CharField(max_length=255, unique=False, blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    observation = models.TextField(null=True, blank=True)

    groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        related_name='pam_user_groups',
        related_query_name='pam_user',
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        related_name='pam_user_permissions',
        related_query_name='pam_user',
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name',]

    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return f'Perfil de {self.user.username}'


class Tenant(models.Model):
    # nome do cliente
    name = models.CharField(max_length=255, unique=True)
    # quem é responsável por validar o pedido de retirada de senha
    validator = models.ForeignKey(User, on_delete=models.PROTECT)
    # status do cliente (ativo ou inativo)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class CloudAccountAccessType(models.Model):
    access_level = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.access_level

class CloudAccount(models.Model):
    ENVIRONMENT_CHOICE = [
        ('dev', 'Development'),
        ('stage', 'Staging'),
        ('prod', 'Production'),
    ]

    CLOUD_PROVIDER = [
        ('aws', 'Amazon Web Services'),
        ('azure', 'Microsoft Azure'),
        ('gcp', 'Google Cloud Platform'),
        ('oci', 'Oracle Cloud Infrastructure'),
    ]

    account = models.CharField(max_length=12)
    tenant = models.ForeignKey(Tenant, on_delete=models.PROTECT)
    provider = models.CharField(max_length=20, choices=CLOUD_PROVIDER, default='aws')
    environment = models.CharField(max_length=20, choices=ENVIRONMENT_CHOICE)
    cloud_username = models.CharField(max_length=255)
    access_level = models.ForeignKey(CloudAccountAccessType, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)
    last_used = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('account', 'provider', 'cloud_username')

        indexes = [
            models.Index(fields=['tenant', 'account', 'provider', 'cloud_username']),
        ]

    def __str__(self):
        return self.tenant.name + ' > ' + self.account + ' > ' + self.provider + ' > ' + self.cloud_username

class PasswordRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('active_window', 'Active Window'),
        ('expired', 'Expired'),
        ('used', 'Used'),
    ]

    # Conta de acesso IAM para a qual a senha está sendo solicitada
    iam_account = models.ForeignKey(CloudAccount, on_delete=models.PROTECT)
    
    # Usuário validador responsável por aprovar ou rejeitar a solicitação
    validator = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='requests_validated'
    )
    
    # Status atual da solicitação
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Duração da janela de tempo solicitada (em horas)
    requested_window = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)]
    )
    
    # Justificativa para a solicitação
    justification = models.TextField(blank=True)
    
    # Horário de início da janela de tempo
    window_start = models.DateTimeField()
    is_withdraw = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    requester = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='password_requests'
    )

    class Meta:
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['iam_account']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(requested_window__range=(1, 4)),
                name='valid_request_window'
            )
        ]
