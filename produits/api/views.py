from rest_framework import viewsets, permissions, filters
from rest_framework.exceptions import PermissionDenied
from ..models import Produit, Categorie
from .serializers import ProduitSerializer, CategorieSerializer


class CategorieViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer
    permission_classes = [permissions.AllowAny]  # Tout le monde peut lire les catégories


class ProduitViewSet(viewsets.ModelViewSet):
    queryset = Produit.objects.select_related('vendeur', 'categorie')
    serializer_class = ProduitSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['translations__titre', 'translations__description']
    ordering_fields = ['prix', 'date_creation']
    ordering = ['-date_creation']

    def get_queryset(self):
        user = self.request.user
        # Si connecté et admin → tout voir
        if user.is_authenticated and getattr(user, 'role', None) == 'ADMIN':
            return Produit.objects.all()
        # Sinon → seulement les produits approuvés (public)
        return Produit.objects.filter(approuve=True)

    def perform_create(self, serializer):
        user = self.request.user

        # 1. Utilisateur non connecté → interdit
        if not user.is_authenticated:
            raise PermissionDenied("Vous devez être connecté pour ajouter un produit.")

        # 2. Vérification du rôle avec getattr pour éviter AttributeError
        user_role = getattr(user, 'role', None)

        if user_role == 'VENDEUR':
            # Optionnel : vérification que le vendeur est approuvé
            user_statut = getattr(user, 'statut', None)
            if user_statut != 'APPROVED':
                raise PermissionDenied("Votre compte vendeur est en attente de validation.")
            serializer.save(vendeur=user)
        elif user_role == 'ADMIN':
            # Les admins peuvent aussi créer des produits si tu veux
            serializer.save(vendeur=user)  # ou sans vendeur si tu préfères
        else:
            # Autres rôles ou aucun rôle → interdit
            raise PermissionDenied("Seuls les vendeurs approuvés peuvent ajouter des produits.")