from rest_framework import viewsets, permissions, filters
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import Produit, Categorie
from .serializers import ProduitSerializer, CategorieSerializer


class CategorieViewSet(viewsets.ModelViewSet):
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionDenied("Seuls les admins peuvent ajouter des catégories.")
        serializer.save()


class ProduitViewSet(viewsets.ModelViewSet):
    serializer_class = ProduitSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['titre', 'description']
    ordering_fields = ['prix', 'date_creation']
    ordering = ['-date_creation']

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Produit.objects.filter(approuve=True)

        if user.is_staff:
            return Produit.objects.all()

        if getattr(user, 'role', None) == 'VENDEUR':
            return Produit.objects.filter(vendeur=user)

        return Produit.objects.filter(approuve=True)

    def perform_create(self, serializer):
        user = self.request.user
        if getattr(user, 'role', None) not in ['VENDEUR', 'ADMIN']:
            raise PermissionDenied("Seuls les vendeurs ou admins peuvent créer des produits.")
        
        # Plus de check sur 'statut' → supprimé car champ inexistant
        serializer.save(vendeur=user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def approve(self, request, pk=None):
        produit = self.get_object()
        produit.approuve = True
        produit.save()
        return Response({'detail': f'Produit {produit.titre} approuvé.'})