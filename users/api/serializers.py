import re
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from djoser.serializers import UserCreateSerializer
from ..models import Utilisateur


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utilisateur
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'entreprise', 'telephone']


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['statut'] = user.statut
        return token


class RegisterSerializer(UserCreateSerializer):
    role = serializers.ChoiceField(choices=['CLIENT', 'VENDEUR'], default='CLIENT')
    telephone = serializers.CharField(max_length=20, required=False, allow_blank=True)

    class Meta(UserCreateSerializer.Meta):
        model = Utilisateur
        fields = ('email', 'password', 'first_name', 'last_name', 'role', 'entreprise', 'telephone')
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
        }

    def validate(self, attrs):
        role = attrs.get('role', 'CLIENT')
        telephone = attrs.get('telephone', '').strip()
        entreprise = attrs.get('entreprise')

        if role == 'VENDEUR' and not telephone:
            raise serializers.ValidationError({"telephone": "Le numéro de téléphone est obligatoire pour les vendeurs."})

        if role == 'VENDEUR' and not entreprise:
            raise serializers.ValidationError({"entreprise": "Le nom de la boutique est obligatoire pour les vendeurs."})

        return attrs

    def create(self, validated_data):
        role = validated_data.pop('role', 'CLIENT')
        entreprise = validated_data.pop('entreprise', None)
        telephone = validated_data.pop('telephone', None)
        email = validated_data['email'].lower().strip()

        # 🔥 TOUS les utilisateurs sont approuvés directement
        statut = 'APPROVED'

        user = Utilisateur.objects.create_user(
            email=email,
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=role,
            statut=statut,
            is_active=True,
            telephone=telephone,
        )

        if entreprise:
            user.entreprise = entreprise
            user.save()

        return user