from rest_framework import serializers
from parler_rest.serializers import TranslatableModelSerializer
from parler_rest.fields import TranslatedFieldsField
from ..models import Produit, Categorie, ProductImage, ProductVariant
from users.api.serializers import UserSerializer
import re


# Serializer personnalisé pour accepter point OU virgule comme séparateur décimal
class DecimalFlexibleField(serializers.DecimalField):
    """
    Accepte les nombres avec point (12.5) ou virgule (12,5)
    Convertit automatiquement la virgule en point avant validation
    """

    def to_internal_value(self, data):
        if isinstance(data, str):
            # Nettoie les espaces
            data = data.strip()

            # Remplace la virgule par un point si c'est le seul séparateur décimal
            if ',' in data and '.' not in data:
                data = data.replace(',', '.', 1)  # Remplace seulement la première virgule

            # Vérifie qu'il ne reste que des chiffres, un point et éventuellement un signe -
            if not re.match(r'^[+-]?\d*\.?\d*$', data):
                self.fail('invalid', msg="Entrée invalide. Utilisez un nombre avec point ou virgule (ex: 12.5 ou 12,5).")

        try:
            return super().to_internal_value(data)
        except Exception:
            self.fail('invalid', msg="Entrée invalide. Utilisez un nombre avec point ou virgule (ex: 12.5 ou 12,5).")


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

    # Champs simples pour création/mise à jour
    nom_du_produit = serializers.CharField(max_length=255, write_only=True)
    description = serializers.CharField(allow_blank=True, required=False, write_only=True)

    # Poids et volume : acceptent point ou virgule, refusent les lettres
    poids = DecimalFlexibleField(
        max_digits=8,
        decimal_places=3,
        required=False,
        allow_null=True,
        min_value=0,
        help_text="Poids en kg (ex: 12.5 ou 12,5)"
    )
    volume = DecimalFlexibleField(
        max_digits=10,
        decimal_places=3,
        required=False,
        allow_null=True,
        min_value=0,
        help_text="Volume en m³ (ex: 1.234 ou 1,234)"
    )

    # Traductions en lecture seulement
    translations = TranslatedFieldsField(shared_model=Produit, read_only=True)

    images = ProductImageSerializer(many=True, read_only=True)
    variantes = ProductVariantSerializer(many=True, read_only=True)

    class Meta:
        model = Produit
        fields = [
            'id', 'translations', 'nom_du_produit', 'description',
            'prix', 'stock', 'poids', 'volume',
            'approuve', 'date_creation', 'vendeur',
            'categorie', 'categorie_id', 'images', 'variantes'
        ]
        read_only_fields = ['approuve', 'date_creation', 'vendeur', 'translations']

    def create(self, validated_data):
        nom_du_produit = validated_data.pop('nom_du_produit')
        description = validated_data.pop('description', '')

        produit = super().create(validated_data)

        produit.set_current_language('fr')
        produit.titre = nom_du_produit
        produit.description = description
        produit.save()

        return produit

    def update(self, instance, validated_data):
        nom_du_produit = validated_data.pop('nom_du_produit', None)
        description = validated_data.pop('description', None)

        instance = super().update(instance, validated_data)

        if nom_du_produit is not None:
            instance.set_current_language('fr')
            instance.titre = nom_du_produit
            if description is not None:
                instance.description = description
            instance.save()

        return instance