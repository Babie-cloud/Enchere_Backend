# produits/api/serializers.py
from rest_framework import serializers
from parler_rest.serializers import TranslatableModelSerializer
from parler_rest.fields import TranslatedFieldsField
from ..models import Produit, Categorie, ProductImage, ProductVariant
from users.api.serializers import UserSerializer
import re

class DecimalFlexibleField(serializers.DecimalField):
    def to_internal_value(self, data):
        if isinstance(data, str):
            data = data.strip().replace(',', '.')
            if not re.match(r'^[+-]?\d*\.?\d*$', data):
                self.fail('invalid')
        return super().to_internal_value(data)

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'ordre']

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id', 'longueur', 'couleur', 'epaisseur', 'reference_sku', 'prix_supplement', 'stock']

class CategorieSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Categorie)
    class Meta:
        model = Categorie
        fields = ['id', 'translations']

class ProduitSerializer(TranslatableModelSerializer):
    vendeur = UserSerializer(read_only=True)
    categorie = CategorieSerializer(read_only=True)
    categorie_id = serializers.PrimaryKeyRelatedField(
        queryset=Categorie.objects.all(),
        source='categorie',
        write_only=True,
        required=False,
        allow_null=True
    )
    
    # Champ pour afficher le nom de la catégorie simplement
    categorie_nom = serializers.SerializerMethodField()

    nom_du_produit = serializers.CharField(max_length=255, write_only=True)
    description = serializers.CharField(allow_blank=True, required=False, write_only=True)

    poids = DecimalFlexibleField(max_digits=8, decimal_places=3, required=False, allow_null=True)
    volume = DecimalFlexibleField(max_digits=10, decimal_places=3, required=False, allow_null=True)

    translations = TranslatedFieldsField(shared_model=Produit, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variantes = ProductVariantSerializer(many=True, read_only=True)

    class Meta:
        model = Produit
        fields = [
            'id', 'translations', 'nom_du_produit', 'description',
            'prix', 'stock', 'poids', 'volume',
            'approuve', 'date_creation', 'vendeur',
            'categorie', 'categorie_nom', 'categorie_id', 
            'images', 'variantes'
        ]
        read_only_fields = ['approuve', 'date_creation', 'vendeur']

    def get_categorie_nom(self, obj):
        if obj.categorie:
            return obj.categorie.safe_translation_getter("nom", language_code='fr')
        return None

    def create(self, validated_data):
        nom = validated_data.pop('nom_du_produit')
        desc = validated_data.pop('description', '')
        produit = super().create(validated_data)
        produit.set_current_language('fr')
        produit.titre = nom
        produit.description = desc
        produit.save()
        return produit

    def update(self, instance, validated_data):
        nom = validated_data.pop('nom_du_produit', None)
        desc = validated_data.pop('description', None)
        instance = super().update(instance, validated_data)
        if nom:
            instance.set_current_language('fr')
            instance.titre = nom
            if desc is not None: instance.description = desc
            instance.save()
        return instance