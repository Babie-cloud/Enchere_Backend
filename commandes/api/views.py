# commandes/api/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models import Panier, PanierItem
from produits.models import Produit
from .serializers import PanierSerializer, PanierItemSerializer

class PanierViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def get_panier(self, request):
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        panier, _ = Panier.objects.get_or_create(session_key=session_key)
        if request.user.is_authenticated and not panier.utilisateur:
            panier.utilisateur = request.user
            panier.save()
        return panier

    def list(self, request):
        panier = self.get_panier(request)
        serializer = PanierSerializer(panier)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def ajouter(self, request):
        panier = self.get_panier(request)
        produit_id = request.data.get('produit_id')
        quantite = int(request.data.get('quantite', 1))

        try:
            produit = Produit.objects.get(id=produit_id, approuve=True)
        except Produit.DoesNotExist:
            return Response({"error": "Produit introuvable ou non approuvé"}, status=404)

        item, created = PanierItem.objects.get_or_create(panier=panier, produit=produit)
        item.quantite += quantite
        item.save()

        return Response(PanierSerializer(panier).data)

    @action(detail=False, methods=['post'])
    def modifier_quantite(self, request):
        """Modifier la quantité d'un produit dans le panier"""
        panier = self.get_panier(request)
        item_id = request.data.get('item_id')
        quantite = int(request.data.get('quantite', 1))

        if quantite < 1:
            return Response({"error": "La quantité doit être au moins 1"}, status=400)

        try:
            item = PanierItem.objects.get(id=item_id, panier=panier)
            item.quantite = quantite
            item.save()
            return Response(PanierSerializer(panier).data)
        except PanierItem.DoesNotExist:
            return Response({"error": "Article non trouvé dans le panier"}, status=404)

    @action(detail=False, methods=['post'])
    def supprimer_item(self, request):
        """Supprimer un produit du panier"""
        panier = self.get_panier(request)
        item_id = request.data.get('item_id')

        try:
            item = PanierItem.objects.get(id=item_id, panier=panier)
            item.delete()
            return Response(PanierSerializer(panier).data)
        except PanierItem.DoesNotExist:
            return Response({"error": "Article non trouvé dans le panier"}, status=404)

    @action(detail=False, methods=['post'])
    def vider(self, request):
        """Vider complètement le panier"""
        panier = self.get_panier(request)
        panier.items.all().delete()
        return Response(PanierSerializer(panier).data)