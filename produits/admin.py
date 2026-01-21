# produits/admin.py
from django.contrib import admin
from parler.admin import TranslatableAdmin
from .models import Categorie, Produit, ProductImage, ProductVariant

@admin.register(Categorie)
class CategorieAdmin(TranslatableAdmin):
    list_display = ('nom',)

# --- Action pour approuver les produits en masse ---
@admin.action(description="Approuver les produits sélectionnés")
def approuver_produits(modeladmin, request, queryset):
    queryset.update(approuve=True)

@admin.register(Produit)
class ProduitAdmin(TranslatableAdmin):
    # On ajoute 'approuver_produits' dans la liste des actions
    actions = [approuver_produits]
    
    # Affichage des colonnes dans la liste
    list_display = ('titre_affichage', 'vendeur', 'prix', 'stock', 'approuve', 'date_creation')
    list_filter = ('approuve', 'categorie', 'vendeur__entreprise')
    search_fields = ('translations__titre', 'vendeur__email')
    
    def titre_affichage(self, obj):
        # Cette méthode assure que le titre s'affiche bien dans l'admin
        return obj.safe_translation_getter("titre", any_language=True) or f"Produit #{obj.pk}"
    
    titre_affichage.short_description = 'Titre' # Nom de la colonne