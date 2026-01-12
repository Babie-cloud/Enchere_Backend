from django.contrib import admin
from parler.admin import TranslatableAdmin
from .models import Categorie, Produit, ProductImage, ProductVariant


@admin.register(Categorie)
class CategorieAdmin(TranslatableAdmin):
    list_display = ('nom',)
    
    # Enlève le bouton "Enregistrer et continuer les modifications"
    save_as_continue = False
    
    # Optionnel : enlève les boutons en haut de page aussi (plus épuré)
    save_on_top = False


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


@admin.register(Produit)
class ProduitAdmin(TranslatableAdmin):
    list_display = ('titre', 'vendeur', 'prix', 'stock', 'approuve', 'date_creation')
    list_filter = ('approuve', 'categorie', 'vendeur__entreprise')
    search_fields = ('translations__titre', 'vendeur__email')
    inlines = [ProductImageInline, ProductVariantInline]
    
    # Optionnel : même chose pour les produits si tu veux moins de boutons
    # save_as_continue = False
    # save_on_top = False