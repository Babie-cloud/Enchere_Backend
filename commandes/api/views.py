# commandes/api/views.py
import uuid
from django.db import transaction
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from produits.models import Produit
from ..models import Panier, PanierItem, Commande, LigneCommande
# Ajoute CommandeSerializer ici (nous allons le créer juste après)
from .serializers import PanierSerializer, PanierItemSerializer, CommandeSerializer

class PanierViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer le panier et passer commande.
    """
    serializer_class = PanierSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Panier.objects.filter(utilisateur=self.request.user)

    def get_object(self):
        """Récupère ou crée le panier de l'utilisateur avec une clé unique."""
        user = self.request.user
        panier = Panier.objects.filter(utilisateur=user).first()
        
        if not panier:
            unique_key = str(uuid.uuid4())[:40]
            panier = Panier.objects.create(
                utilisateur=user,
                session_key=unique_key
            )
        return panier

    def create(self, request, *args, **kwargs):
        """Évite l'erreur d'unicité sur le POST racine."""
        panier = self.get_object()
        serializer = self.get_serializer(panier)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def my_cart(self, request):
        panier = self.get_object()
        serializer = self.get_serializer(panier)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='ajouter')
    def ajouter(self, request):
        produit_id = request.data.get('produit_id')
        try:
            quantite = int(request.data.get('quantite', 1))
        except (ValueError, TypeError):
            raise ValidationError("La quantité doit être un nombre valide.")

        if quantite < 1:
            raise ValidationError("La quantité doit être positive.")

        # On vérifie que le produit est approuvé (le fameux bouton vert !)
        produit = get_object_or_404(Produit, id=produit_id, approuve=True)
        panier = self.get_object()

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

    @action(detail=False, methods=['post'], url_path='valider-commande')
    def passer_commande(self, request):
        """
        Transforme le panier en commande et vide le panier.
        """
        panier = self.get_object()
        items = panier.items.all()

        if not items.exists():
            return Response({"error": "Le panier est vide"}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            commande = Commande.objects.create(
                client=request.user,
                payee=False
            )

            for item in items:
                LigneCommande.objects.create(
                    commande=commande,
                    produit=item.produit,
                    quantite=item.quantite,
                    prix_unitaire=item.produit.prix
                )

            items.delete()

        return Response({
            "message": "Commande créée avec succès",
            "commande_id": commande.id
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['delete'], url_path='vider')
    def vider(self, request):
        panier = self.get_object()
        panier.items.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommandeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour consulter l'historique des commandes passées.
    """
    serializer_class = CommandeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # L'utilisateur ne voit que ses propres commandes
        return Commande.objects.filter(client=self.request.user).order_by('-date_commande')