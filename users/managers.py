from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, username=None, **extra_fields):
        if not email:
            raise ValueError(_('L\'email doit être renseigné'))

        email = self.normalize_email(email)

        if not username:
            username = email.split('@')[0]

        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, username=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)   # ← important
        extra_fields.setdefault('role', 'ADMIN')
        extra_fields.setdefault('statut', 'APPROVED')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser doit avoir is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser doit avoir is_superuser=True.')
        if extra_fields.get('is_active') is not True:
            raise ValueError('Superuser doit avoir is_active=True.')

        if not username:
            username = email.split('@')[0]

        return self.create_user(
            email=email,
            password=password,
            username=username,
            **extra_fields
        )