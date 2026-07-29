# core/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view
from rest_framework.response import Response

from produits.api.views import ProduitViewSet, CategorieViewSet
from commandes.api.views import PanierViewSet, CommandeViewSet I

router = DefaultRouter()
router.register(r'api/produits', ProduitViewSet, basename='produit')
router.register(r'api/categories', CategorieViewSet, basename='categorie')
router.register(r'api/panier', PanierViewSet, basename='panier')
router.register(r'api/commandes', CommandeViewSet, basename='commande') 

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'produits': request.build_absolute_uri('/api/produits/'),
        'catégories': request.build_absolute_uri('/api/categories/'),
        'panier': request.build_absolute_uri('/api/panier/'),
        'mes-commandes': request.build_absolute_uri('/api/commandes/'), 
        'inscription': request.build_absolute_uri('/api/auth/users/'),
        'connexion JWT': request.build_absolute_uri('/api/auth/jwt/create/'),
        'rafraîchir token': request.build_absolute_uri('/api/auth/jwt/refresh/'),
        'profil': request.build_absolute_uri('/api/auth/users/me/'),
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', api_root, name='api-root'),
    path('api/auth/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.jwt')),
    path('', include(router.urls)),
]
