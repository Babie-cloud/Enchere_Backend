# commandes/api/serializers.py
from rest_framework import serializers
from ..models import Panier, PanierItem
from produits.models import Produit  # ← Produit vient de produits
# Plus besoin de Categorie, ProductImage, ProductVariant ici pour l'instant
from produits.api.serializers import ProduitSerializer  # si tu l'utilises


class PanierItemSerializer(serializers.ModelSerializer):
    produit = ProduitSerializer(read_only=True)
    produit_id = serializers.PrimaryKeyRelatedField(
        queryset=Produit.objects.filter(approuve=True),
        source='produit',
        write_only=True
    )
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = PanierItem
        fields = ['id', 'produit', 'produit_id', 'quantite', 'subtotal']

    def get_subtotal(self, obj):
        return obj.subtotal()


# Dans commandes/api/serializers.py
class PanierSerializer(serializers.ModelSerializer):
    items = PanierItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Panier
        fields = ['id', 'items', 'total']

    def get_total(self, obj):
        # Utilise la relation 'items' définie dans le modèle PanierItem
        return sum(item.subtotal() for item in obj.items.all())