# produits/api/serializers.py
from rest_framework import serializers
import json

from ..models import Produit, Categorie, ProductImage, ProductVariant
from users.api.serializers import UserSerializer


class DecimalFlexibleField(serializers.DecimalField):
    """Permet d'accepter des strings avec virgule comme séparateur décimal"""
    def to_internal_value(self, data):
        if isinstance(data, str):
            data = data.strip().replace(',', '.')
        return super().to_internal_value(data)


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'ordre']
        read_only_fields = ['id']


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id', 'longueur', 'couleur', 'epaisseur', 'reference_sku', 'prix_supplement', 'stock']


class CategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorie
        fields = ['id', 'nom']


class ProduitSerializer(serializers.ModelSerializer):
    """
    Serializer principal pour Produit (liste, détail, création, mise à jour)
    """
    vendeur = UserSerializer(read_only=True)
    categorie = CategorieSerializer(read_only=True)
    
    # Pour l'écriture de la catégorie (on accepte l'ID)
    categorie_id = serializers.PrimaryKeyRelatedField(
        queryset=Categorie.objects.all(),
        source='categorie',
        write_only=True,
        required=False,
        allow_null=True
    )

    images = ProductImageSerializer(many=True, read_only=True)
    variantes = ProductVariantSerializer(many=True, read_only=True)

    class Meta:
        model = Produit
        fields = [
            'id',
            'titre',
            'description',
            'prix',
            'stock',
            'poids',
            'volume',
            'approuve',
            'date_creation',
            'vendeur',
            'categorie',
            'categorie_id',
            'images',
            'variantes',
        ]
        read_only_fields = [
            'approuve',
            'date_creation',
            'vendeur',
        ]
        extra_kwargs = {
            'titre': {'required': True},
            'description': {'required': False, 'allow_blank': True},
        }

    def create(self, validated_data):
        """
        Création d'un produit + gestion des images uploadées
        """
        images_files = self.context['request'].FILES.getlist('images_files')
        images_meta_json = self.context['request'].data.get('images', '[]')

        try:
            images_meta = json.loads(images_meta_json)
        except json.JSONDecodeError:
            raise serializers.ValidationError({"images": "Format JSON invalide pour les métadonnées images"})

        # Création du produit
        produit = super().create(validated_data)

        # Gestion des images
        for idx, meta in enumerate(images_meta):
            if idx < len(images_files):
                ProductImage.objects.create(
                    produit=produit,
                    image=images_files[idx],
                    alt_text=meta.get('alt_text', ''),
                    ordre=meta.get('ordre', idx)
                )

        return produit

    def update(self, instance, validated_data):
        """
        Mise à jour + remplacement complet des images si fourni
        """
        images_files = self.context['request'].FILES.getlist('images_files')
        images_meta_json = self.context['request'].data.get('images')

        # Mise à jour des champs classiques
        instance = super().update(instance, validated_data)

        # Si on envoie de nouvelles images ou métadonnées → on remplace tout
        if images_files or images_meta_json:
            instance.images.all().delete()  # suppression complète

            if images_meta_json:
                try:
                    images_meta = json.loads(images_meta_json)
                except json.JSONDecodeError:
                    raise serializers.ValidationError({"images": "Format JSON invalide"})

                for idx, meta in enumerate(images_meta):
                    if idx < len(images_files):
                        ProductImage.objects.create(
                            produit=instance,
                            image=images_files[idx],
                            alt_text=meta.get('alt_text', ''),
                            ordre=meta.get('ordre', idx)
                        )
                    # Option : si on veut conserver des anciennes images non remplacées,
                    # on peut ajouter une logique avec meta.get('id') ici

        return instance