# commandes/admin.py
from django.contrib import admin
from .models import Commande, LigneCommande

@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'date_commande', 'payee', 'stripe_id')
    list_filter = ('payee', 'date_commande')

@admin.register(LigneCommande)
class LigneCommandeAdmin(admin.ModelAdmin):
    list_display = ('commande', 'produit', 'quantite', 'prix_unitaire')