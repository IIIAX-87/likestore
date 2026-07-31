"""
Users app - models for user management.
"""
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Custom user manager."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model with email authentication."""

    # Fix reverse accessor conflicts with Django's auth.User
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('Groups'),
        blank=True,
        help_text=_('Groups this user belongs to.'),
        related_name='likestore_user_set',  # Changed from default 'user_set'
        related_query_name='likestore_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('User permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name='likestore_user_set',  # Changed from default 'user_set'
        related_query_name='likestore_user',
    )
    """Custom user model with email authentication."""

    email = models.EmailField(_('Email'), unique=True)
    first_name = models.CharField(_('First name'), max_length=150, blank=True)
    last_name = models.CharField(_('Last name'), max_length=150, blank=True)
    phone = models.CharField(_('Phone'), max_length=20, blank=True)

    is_active = models.BooleanField(_('Is active'), default=True)
    is_staff = models.BooleanField(_('Is staff'), default=False)

    date_joined = models.DateTimeField(_('Date joined'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)

    # Profile fields
    avatar = models.ImageField(_('Avatar'), upload_to='users/avatars/', null=True, blank=True)
    birthday = models.DateField(_('Birthday'), null=True, blank=True)
    gender = models.CharField(_('Gender'), max_length=10, choices=[
        ('male', 'Мужской'),
        ('female', 'Женский'),
    ], blank=True)

    # Notification preferences
    notify_orders = models.BooleanField(_('Notify about orders'), default=True)
    notify_promotions = models.BooleanField(_('Notify about promotions'), default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        indexes = [
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return self.email

    def get_full_name(self):
        full_name = f'{self.first_name} {self.last_name}'.strip()
        return full_name or self.email

    def get_short_name(self):
        return self.first_name or self.email.split('@')[0]


class Address(models.Model):
    """User address model."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='addresses',
        verbose_name=_('User')
    )
    name = models.CharField(_('Address name'), max_length=100, default='Домашний')
    city = models.CharField(_('City'), max_length=200)
    street = models.CharField(_('Street'), max_length=300)
    house = models.CharField(_('House'), max_length=50)
    apartment = models.CharField(_('Apartment'), max_length=50, blank=True)
    postal_code = models.CharField(_('Postal code'), max_length=10, blank=True)
    comment = models.TextField(_('Comment'), blank=True)
    is_default = models.BooleanField(_('Is default'), default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Address')
        verbose_name_plural = _('Addresses')

    def __str__(self):
        return f'{self.name} - {self.city}, {self.street}'


class PasswordReset(models.Model):
    """Password reset tokens."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='password_resets',
        verbose_name=_('User')
    )
    token = models.CharField(_('Token'), max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(_('Expires at'))
    used = models.BooleanField(_('Used'), default=False)

    class Meta:
        verbose_name = _('Password reset')
        verbose_name_plural = _('Password resets')

    def __str__(self):
        return f'{self.user.email} - {self.token}'
