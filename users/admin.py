from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Utilisateur


# @admin.register(Utilisateur)
# class UtilisateurAdmin(BaseUserAdmin):
#     list_display = ('email', 'username', 'first_name', 'last_name', 'role', 'statut', 'is_staff')
#     list_filter = ('role', 'is_staff', 'is_active')  # statut retiré du filter car toujours APPROVED
#     search_fields = ('email', 'username', 'first_name', 'last_name')
#     ordering = ('email',)

#     fieldsets = (
#         (None, {'fields': ('username', 'password')}),
#         ('Informations personnelles', {'fields': ('first_name', 'last_name', 'email')}),
#         ('Rôle & Statut', {'fields': ('role', 'statut')}),
#         ('Entreprise', {'fields': ('entreprise',)}),
#         ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
#         ('Dates', {'fields': ('last_login', 'date_joined')}),
#     )
@admin.register(Utilisateur)
class UtilisateurAdmin(BaseUserAdmin):
    list_display = (
        'email',
        'username',
        'first_name',
        'last_name',
        'role',
        'statut',
        'is_staff',
        'is_superuser',       # ← très important !
        'is_active'
    )
    list_display_links = ('email',)  # cliquable pour modifier
    list_filter = ('role', 'statut', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email',)

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'statut'),
        }),
    )