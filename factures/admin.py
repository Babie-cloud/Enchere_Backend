# factures/admin.py
from django.contrib import admin
from .models import Facture

@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    list_display = ('numero_facture', 'commande', 'date_emission', 'date_echeance')
    readonly_fields = ('numero_facture', 'date_emission')