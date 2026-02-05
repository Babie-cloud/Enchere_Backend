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
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'ordre']
        read_only_fields = ['id']

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id', 'longueur', 'couleur', 'epaisseur', 'reference_sku', 'prix_supplement', 'stock']


class CategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorie
        fields = ['id', 'nom']


class ProduitSerializer(serializers.ModelSerializer):
    vendeur = UserSerializer(read_only=True)
    categorie = CategorieSerializer(read_only=True)
    
    categorie_id = serializers.PrimaryKeyRelatedField(
        queryset=Categorie.objects.all(),
        source='categorie',
        write_only=True,
        required=False,
        allow_null=True
    )

    categorie_nom = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True
    )

    images = ProductImageSerializer(many=True, read_only=True)
    variantes = ProductVariantSerializer(many=True, read_only=True)

    class Meta:
        model = Produit
        fields = [
            'id', 'titre', 'description', 'prix', 'stock', 'poids', 'volume',
            'approuve', 'date_creation', 'vendeur', 'categorie',
            'categorie_id', 'categorie_nom', 'images', 'variantes',
        ]
        read_only_fields = ['date_creation', 'vendeur']
        extra_kwargs = {
            'titre': {'required': True},
            'description': {'required': False, 'allow_blank': True},
        }

    def validate(self, data):
        # Sécurité : les vendeurs ne peuvent pas s'auto-approuver
        user = self.context['request'].user
        if data.get('approuve') is True and not user.is_staff:
            data['approuve'] = False
        return data

    def create(self, validated_data):
        categorie_nom = validated_data.pop('categorie_nom', None)
        if categorie_nom and not validated_data.get('categorie'):
            try:
                categorie = Categorie.objects.get(nom__iexact=categorie_nom.strip())
                validated_data['categorie'] = categorie
            except Categorie.DoesNotExist:
                raise serializers.ValidationError({
                    "categorie": f"La catégorie '{categorie_nom}' n'existe pas."
                })

        images_files = self.context['request'].FILES.getlist('images_files')
        images_meta_json = self.context['request'].data.get('images', '[]')

        try:
            images_meta = json.loads(images_meta_json)
        except json.JSONDecodeError:
            raise serializers.ValidationError({"images": "Format JSON invalide pour les métadonnées images"})

        produit = super().create(validated_data)

        for idx, meta in enumerate(images_meta):
            if idx < len(images_files):
                ProductImage.objects.create(
                    produit=produit,
                    image=images_files[idx],
                    alt_text=meta.get('alt_text', ''),
                    ordre=meta.get('ordre', idx)
                )

        return produit