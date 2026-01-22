from rest_framework import serializers
from parler_rest.serializers import TranslatableModelSerializer
from parler_rest.fields import TranslatedFieldsField
from ..models import Produit, Categorie, ProductImage, ProductVariant
from users.api.serializers import UserSerializer
import json

class DecimalFlexibleField(serializers.DecimalField):
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
    categorie_nom = serializers.SerializerMethodField()

    nom_du_produit = serializers.CharField(max_length=255, write_only=True, required=True)
    description = serializers.CharField(allow_blank=True, required=False, write_only=True)

    poids = DecimalFlexibleField(max_digits=8, decimal_places=3, required=False, allow_null=True)
    volume = DecimalFlexibleField(max_digits=10, decimal_places=3, required=False, allow_null=True)

    translations = TranslatedFieldsField(shared_model=Produit, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)  # read_only ici, on gère manuellement dans create/update

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

        images_meta = []
        images_files = self.context['request'].FILES.getlist('images_files')

        # Récupérer le JSON meta des images
        images_json = self.context['request'].data.get('images')
        if images_json:
            try:
                images_meta = json.loads(images_json)
            except:
                raise serializers.ValidationError({"images": "Format JSON invalide pour les métadonnées images"})

        produit = super().create(validated_data)
        produit.set_current_language('fr')
        produit.titre = nom
        produit.description = desc
        produit.save()

        # Création des images
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
        nom = validated_data.pop('nom_du_produit', None)
        desc = validated_data.pop('description', None)

        images_meta = []
        images_files = self.context['request'].FILES.getlist('images_files')

        images_json = self.context['request'].data.get('images')
        if images_json:
            try:
                images_meta = json.loads(images_json)
            except:
                raise serializers.ValidationError({"images": "Format JSON invalide"})

        instance = super().update(instance, validated_data)

        if nom:
            instance.set_current_language('fr')
            instance.titre = nom
            if desc is not None:
                instance.description = desc
            instance.save()

        # Gestion images en update : on remplace tout pour simplifier
        if 'images' in self.context['request'].data or images_files:
            instance.images.all().delete()

            for idx, meta in enumerate(images_meta):
                if idx < len(images_files):
                    ProductImage.objects.create(
                        produit=instance,
                        image=images_files[idx],
                        alt_text=meta.get('alt_text', ''),
                        ordre=meta.get('ordre', idx)
                    )
                elif 'id' in meta:
                    # Conserver image existante si id présent (pas de nouveau fichier)
                    try:
                        old_img = ProductImage.objects.get(id=meta['id'], produit=instance)
                        ProductImage.objects.create(
                            produit=instance,
                            image=old_img.image,  # réutilise le fichier existant
                            alt_text=meta.get('alt_text', old_img.alt_text),
                            ordre=meta.get('ordre', old_img.ordre)
                        )
                    except ProductImage.DoesNotExist:
                        pass

        return instance