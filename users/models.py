import re
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager


class Utilisateur(AbstractUser):
    """
    Modèle utilisateur personnalisé pour DirectAlu
    - Connexion par email uniquement
    - Username généré automatiquement et unique
    - Rôles : CLIENT ou VENDEUR (ADMIN possible via createsuperuser)
    - Statut : toujours APPROVED désormais
    """

    ROLE_CHOICES = [
        ('CLIENT', 'Client'),
        ('VENDEUR', 'Vendeur'),
        ('ADMIN', 'Administrateur'),  # Ajouté pour plus de clarté
    ]

    STATUT_CHOICES = [
        ('PENDING', 'En attente'),
        ('APPROVED', 'Approuvé'),
    ]

    # Champs personnalisés
    email = models.EmailField(
        _('email address'),
        unique=True,
        error_messages={
            'unique': _("Un utilisateur avec cet email existe déjà."),
        },
    )

    username = models.CharField(
        max_length=150,
        unique=True,
        blank=True,
        null=True,
        help_text=_("Nom d'utilisateur généré automatiquement à partir de l'email."),
        error_messages={
            'unique': _("Ce nom d'utilisateur est déjà pris."),
        },
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='CLIENT',
    )

    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='APPROVED',
    )

    entreprise = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Nom de l'entreprise / boutique"
    )

    telephone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Téléphone"
    )

    # Manager personnalisé
    objects = CustomUserManager()

    # Configuration pour l'authentification
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # plus besoin de username ou autres

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
        ordering = ['email']

    def __str__(self):
        return self.email or "Utilisateur sans email"

    def save(self, *args, **kwargs):
        """
        Génération automatique du username à partir de l'email si non fourni
        """
        if self.email and not self.username:
            # On prend la partie avant @, on nettoie et on met en minuscule
            base = re.sub(r'[^a-zA-Z0-9]', '', self.email.split('@')[0].lower())
            username = base
            counter = 1

            # On s'assure de l'unicité
            while Utilisateur.objects.filter(username=username).exists():
                username = f"{base}{counter}"
                counter += 1

            self.username = username

        super().save(*args, **kwargs)   