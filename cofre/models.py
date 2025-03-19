from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        username = email.split("@")[0]
        user = self.model(
            email=email,
            username=username,
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
    role = models.CharField(max_length=20, choices=ROLE_CHOICE)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        related_name='cofre_user_groups',
        related_query_name='cofre_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        related_name='cofre_user_permissions',
        related_query_name='cofre_user',
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

class Tenant(models.Model):

    ENVIRONMENT_CHOICE = [
        ('dev', 'Development'),
        ('stage', 'Staging'),
        ('prod', 'Production'),
    ]

    name = models.CharField(max_length=255)
    aws_account_id= models.CharField(max_length=12, unique=True)
    environment = models.CharField(max_length=20 ,choices=ENVIRONMENT_CHOICE)
    status = models.CharField(max_length=20, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class UserTenant(models.Model):

    user = models.ForeignKey(User, on_delete=models.PROTECT)
    tenant = models.ForeignKey(Tenant, on_delete=models.PROTECT)

    class Meta:
        unique_together = ('user', 'tenant')

class IAMAccount(models.Model):
    ACCESS_LEVEL_CHOICES = [
        ('read', 'Read'),
        ('admin', 'Admin'),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.PROTECT)
    username = models.CharField(max_length=255)
    access_level = models.CharField(max_length=20, choices=ACCESS_LEVEL_CHOICES)
    status = models.CharField(max_length=20, default='active')
    expiry_date = models.DateTimeField()
    last_rotated = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('tenant', 'username')
        indexes = [
            models.Index(fields=['expiry_date']),
        ]

class PasswordRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('active_window', 'Active Window'),
        ('expired', 'Expired'),
        ('used', 'Used'),
    ]

    iam_account = models.ForeignKey(IAMAccount, on_delete=models.PROTECT)
    validator = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='requests_validated'
    )
    status = models.CharField(max_length=20, default='active')
    requested_window = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)]
    )
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
                check=models.Q(requested_window__range=(1,4)),
                name='valid_request_window'
            )
        ]




