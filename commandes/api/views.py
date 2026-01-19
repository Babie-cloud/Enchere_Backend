# commandes/api/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from produits.models import Produit
from ..models import Panier, PanierItem   # ← assume ces models existent
from .serializers import PanierSerializer, PanierItemSerializer


class PanierViewSet(viewsets.ModelViewSet):
    serializer_class = PanierSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Uniquement le panier de l'utilisateur connecté
        return Panier.objects.filter(utilisateur=self.request.user)

    def get_object(self):
        # Retourne toujours le panier de l'utilisateur (pas besoin d'ID dans l'URL)
        panier, created = Panier.objects.get_or_create(utilisateur=self.request.user)
        return panier

    @action(detail=False, methods=['get'])
    def my_cart(self, request):
        panier = self.get_object()
        serializer = self.get_serializer(panier)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='ajouter')
    def ajouter(self, request):
        produit_id = request.data.get('produit_id')
        quantite = int(request.data.get('quantite', 1))

        if quantite < 1:
            raise ValidationError("La quantité doit être positive.")

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

    @action(detail=False, methods=['patch'], url_path='items/(?P<item_id>\\d+)')
    def modifier_item(self, request, item_id=None):
        item = get_object_or_404(PanierItem, id=item_id, panier__utilisateur=request.user)
        quantite = request.data.get('quantite')

        if quantite is not None:
            if int(quantite) < 1:
                item.delete()
            else:
                item.quantite = int(quantite)
                item.save()

        serializer = PanierSerializer(item.panier)
        return Response(serializer.data)

    @action(detail=False, methods=['delete'], url_path='items/(?P<item_id>\\d+)')
    def supprimer_item(self, request, item_id=None):
        item = get_object_or_404(PanierItem, id=item_id, panier__utilisateur=request.user)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['delete'], url_path='vider')
    def vider(self, request):
        panier = self.get_object()
        panier.items.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)