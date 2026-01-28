# produits/admin.py

from django.contrib import admin
# from parler.admin import TranslatableAdmin   ← SUPPRIME CETTE LIGNE

from .models import Categorie, Produit, ProductImage, ProductVariant


@admin.action(description="Approuver les produits sélectionnés")
def approuver_produits(modeladmin, request, queryset):
    queryset.update(approuve=True)


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):           # ← remplace TranslatableAdmin par admin.ModelAdmin
    list_display = ('nom',)


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):              # ← remplace TranslatableAdmin par admin.ModelAdmin
    actions = [approuver_produits]
    
    list_display = ('titre', 'vendeur', 'prix', 'stock', 'approuve', 'date_creation')
    list_filter = ('approuve', 'categorie', 'vendeur__entreprise')   # ← attention : vendeur__entreprise peut ne plus exister si ton User n'a plus ce champ
    search_fields = ('titre', 'vendeur__email')
    
    # Si tu avais une méthode titre_affichage, adapte-la ou supprime-la
    # def titre_affichage(self, obj):
    #     return obj.titre
    # titre_affichage.short_description = 'Titre'


# Optionnel : enregistre les autres modèles si tu veux les voir dans l'admin
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('produit', 'ordre', 'alt_text')
    list_filter = ('produit',)


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('produit', 'reference_sku', 'stock', 'couleur')
    list_filter = ('produit',)