# commandes/api/views.py
import uuid
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from produits.models import Produit
from ..models import Panier, PanierItem 
from .serializers import PanierSerializer, PanierItemSerializer

class PanierViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer le panier de l'utilisateur connecté.
    """
    serializer_class = PanierSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Retourne uniquement le panier de l'utilisateur connecté
        return Panier.objects.filter(utilisateur=self.request.user)

    def get_object(self):
        """
        Récupère le panier de l'utilisateur. 
        Si aucun panier n'existe, en crée un avec une clé unique (UUID).
        """
        user = self.request.user
        
        # 1. On cherche si un panier existe déjà pour cet utilisateur
        panier = Panier.objects.filter(utilisateur=user).first()
        
        if not panier:
            # 2. Si non, on le crée. On génère un UUID pour la session_key 
            # afin d'éviter les erreurs d'unicité (IntegrityError).
            unique_key = str(uuid.uuid4())[:40]
            panier = Panier.objects.create(
                utilisateur=user,
                session_key=unique_key
            )
            
        return panier

    def create(self, request, *args, **kwargs):
        """
        Redéfinition du POST sur /api/panier/
        Renvoie le panier existant au lieu de tenter une création aveugle.
        """
        panier = self.get_object()
        serializer = self.get_serializer(panier)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def my_cart(self, request):
        """URL: /api/panier/my_cart/"""
        panier = self.get_object()
        serializer = self.get_serializer(panier)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='ajouter')
    def ajouter(self, request):
        """URL: /api/panier/ajouter/"""
        produit_id = request.data.get('produit_id')
        
        try:
            quantite = int(request.data.get('quantite', 1))
        except (ValueError, TypeError):
            raise ValidationError("La quantité doit être un nombre valide.")

        if quantite < 1:
            raise ValidationError("La quantité doit être positive.")

        # On vérifie que le produit existe et est approuvé
        produit = get_object_or_404(Produit, id=produit_id, approuve=True)
        panier = self.get_object()

        # Ajout ou mise à jour de l'article dans le panier
        item, created = PanierItem.objects.get_or_create(
            panier=panier,
            produit=produit,
            defaults={'quantite': quantite}
        )

        if not created:
            item.quantite += quantite
            item.save()

        serializer = PanierSerializer(panier)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['patch'], url_path='items/(?P<item_id>\\d+)')
    def modifier_item(self, request, item_id=None):
        """URL: /api/panier/items/{id}/ (PATCH)"""
        panier = self.get_object()
        item = get_object_or_404(PanierItem, id=item_id, panier=panier)
        quantite = request.data.get('quantite')

        if quantite is not None:
            try:
                q = int(quantite)
                if q < 1:
                    item.delete()
                else:
                    item.quantite = q
                    item.save()
            except ValueError:
                raise ValidationError("Quantité invalide.")

        serializer = PanierSerializer(panier)
        return Response(serializer.data)

    @action(detail=False, methods=['delete'], url_path='items/(?P<item_id>\\d+)')
    def supprimer_item(self, request, item_id=None):
        """URL: /api/panier/items/{id}/ (DELETE)"""
        panier = self.get_object()
        item = get_object_or_404(PanierItem, id=item_id, panier=panier)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['delete'], url_path='vider')
    def vider(self, request):
        """URL: /api/panier/vider/"""
        panier = self.get_object()
        panier.items.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)