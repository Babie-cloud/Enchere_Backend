# produits/api/views.py
from rest_framework import viewsets, permissions, filters
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models import Produit, Categorie
from .serializers import ProduitSerializer, CategorieSerializer

class CategorieViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer
    permission_classes = [permissions.AllowAny]

class ProduitViewSet(viewsets.ModelViewSet):
    queryset = Produit.objects.select_related('vendeur', 'categorie')
    serializer_class = ProduitSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['translations__titre', 'translations__description']
    ordering_fields = ['prix', 'date_creation']
    ordering = ['-date_creation']

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and getattr(user, 'role', None) == 'ADMIN':
            return Produit.objects.all()  # Admin voit tout
        elif user.is_authenticated and getattr(user, 'role', None) == 'VENDEUR':
            return Produit.objects.filter(vendeur=user)  # Vendeur voit seulement les siens
        else:
            return Produit.objects.filter(approuve=True)  # Public voit seulement approuvés

    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_authenticated:
            raise PermissionDenied("Vous devez être connecté.")
        user_role = getattr(user, 'role', None)
        if user_role not in ['VENDEUR', 'ADMIN']:
            raise PermissionDenied("Seuls les vendeurs ou admins peuvent ajouter des produits.")
        if user_role == 'VENDEUR' and getattr(user, 'statut', None) != 'APPROVED':
            raise PermissionDenied("Votre compte vendeur est en attente.")
        serializer.save(vendeur=user)

    # Nouvelle action : approuver un produit (seulement pour admins)
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def approve(self, request, pk=None):
        produit = self.get_object()
        produit.approuve = True
        produit.save()
        return Response({'detail': f'Produit {produit} approuvé avec succès.'})