from django.contrib import admin
from .models import Categorie, Produit, ProductImage, ProductVariant


@admin.action(description="Approuver les produits sélectionnés")
def approuver_produits(modeladmin, request, queryset):
    queryset.update(approuve=True)


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom',)
    search_fields = ('nom',)


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    actions = [approuver_produits]
    
    list_display = ('titre', 'vendeur', 'prix', 'stock', 'approuve', 'date_creation')
    list_filter = ('approuve', 'categorie')
    search_fields = ('titre', 'vendeur__email', 'vendeur__username')
    date_hierarchy = 'date_creation'


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('produit', 'ordre', 'alt_text')
    list_filter = ('produit',)
    search_fields = ('produit__titre', 'alt_text')


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('produit', 'reference_sku', 'stock', 'couleur')
    list_filter = ('produit',)
    search_fields = ('produit__titre', 'reference_sku')