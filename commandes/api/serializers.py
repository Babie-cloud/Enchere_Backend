# commandes/api/serializers.py
from rest_framework import serializers
from ..models import Panier, PanierItem, Commande, LigneCommande
from produits.models import Produit
from produits.api.serializers import ProduitSerializer

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

class PanierSerializer(serializers.ModelSerializer):
    items = PanierItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Panier
        fields = ['id', 'items', 'total']

    def get_total(self, obj):
        return sum(item.subtotal() for item in obj.items.all())

# --- NOUVEAUX SERIALIZERS POUR LES COMMANDES ---

class LigneCommandeSerializer(serializers.ModelSerializer):
    produit_nom = serializers.SerializerMethodField()
    
    class Meta:
        model = LigneCommande
        fields = ['id', 'produit', 'produit_nom', 'quantite', 'prix_unitaire', 'get_total']

    def get_produit_nom(self, obj):
        return obj.produit.safe_translation_getter("titre", any_language=True)

class CommandeSerializer(serializers.ModelSerializer):
    lignes = LigneCommandeSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Commande
        fields = ['id', 'date_commande', 'payee', 'statut', 'lignes', 'total']

    def get_total(self, obj):
        # Utilise la méthode get_total définie dans ton modèle Commande
        return sum(ligne.get_total() for ligne in obj.lignes.all())