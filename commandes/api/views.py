# commandes/api/views.py
# commandes/api/views.py - imports corrigés

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response           # ← R majuscule obligatoire
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.shortcuts import get_object_or_404
from django.db import transaction


from ..models import Panier, PanierItem
from produits.models import Produit
from .serializers import PanierSerializer, PanierItemSerializer
from produits.models import Produit


class PanierViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer le panier de l'utilisateur connecté.
    - Un seul panier par utilisateur (OneToOne)
    - Support session_key pour visiteurs non connectés (optionnel, à implémenter si besoin)
    """
    serializer_class = PanierSerializer
    permission_classes = [permissions.IsAuthenticated]  # Tout nécessite login ici

    def get_queryset(self):
        # Seulement le panier de l'utilisateur courant
        return Panier.objects.filter(utilisateur=self.request.user)

    def get_object(self):
        # Récupère ou crée le panier de l'utilisateur si inexistant
        panier, created = Panier.objects.get_or_create(
            utilisateur=self.request.user,
            defaults={'session_key': None}  # session_key plus utilisé ici
        )
        return panier

    def list(self, request, *args, **kwargs):
        # Retourne directement le panier unique (pas une liste)
        panier = self.get_object()
        serializer = self.get_serializer(panier)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        """Alias pour récupérer le panier courant de l'utilisateur"""
        return self.list(request)

    @action(detail=False, methods=['post'], url_path='add')
    @transaction.atomic
    def add(self, request):
        """
        Ajoute un produit au panier (ou incrémente la quantité si déjà présent)
        Exemple body :
        {
            "produit_id": 5,
            "quantite": 2   // optionnel, défaut 1
        }
        """
        produit_id = request.data.get('produit_id')
        quantite = int(request.data.get('quantite', 1))

        if quantite < 1:
            raise ValidationError({"quantite": "Doit être >= 1"})

        produit = get_object_or_404(Produit, id=produit_id, approuve=True)

        panier = self.get_object()

        # Vérifie stock disponible (optionnel mais recommandé)
        if produit.stock < quantite:
            raise ValidationError({"detail": f"Stock insuffisant pour {produit} (dispo: {produit.stock})"})

        item, created = PanierItem.objects.get_or_create(
            panier=panier,
            produit=produit,
            defaults={'quantite': quantite}
        )

        if not created:
            # Incrémente si existe déjà
            item.quantite += quantite
            if item.quantite > produit.stock:
                raise ValidationError({"detail": "Quantité dépasse le stock disponible"})
            item.save()

        serializer = PanierSerializer(panier)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='remove')
    def remove(self, request):
        """
        Supprime un item du panier ou réduit sa quantité
        Exemple body :
        {
            "produit_id": 5,
            "quantite": 1   // optionnel, si non fourni → supprime tout l'item
        }
        """
        produit_id = request.data.get('produit_id')
        quantite_a_enlever = int(request.data.get('quantite', 999999))  # gros nombre = tout supprimer

        if not produit_id:
            raise ValidationError({"produit_id": "Obligatoire"})

        panier = self.get_object()
        item = get_object_or_404(PanierItem, panier=panier, produit_id=produit_id)

        if quantite_a_enlever >= item.quantite:
            item.delete()
        else:
            item.quantite -= quantite_a_enlever
            item.save()

        serializer = PanierSerializer(panier)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='clear')
    def clear(self, request):
        """Vide complètement le panier"""
        panier = self.get_object()
        panier.items.all().delete()
        serializer = PanierSerializer(panier)
        return Response(serializer.data)

    # Optionnel : désactiver create/update/destroy standards si tu gères via actions
    def create(self, request, *args, **kwargs):
        return Response({"detail": "Utilisez l'action 'add' pour ajouter au panier"}, status=405)

    def update(self, request, *args, **kwargs):
        return Response({"detail": "Mise à jour directe interdite, utilisez les actions add/remove"}, status=405)

    def destroy(self, request, *args, **kwargs):
        return Response({"detail": "Suppression directe interdite, utilisez clear ou remove"}, status=405)