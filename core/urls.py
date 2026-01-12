# core/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Nos ViewSets
from produits.api.views import ProduitViewSet, CategorieViewSet
from commandes.api.views import PanierViewSet

# Router
router = DefaultRouter()
router.register(r'api/produits', ProduitViewSet, basename='produit')
router.register(r'api/categories', CategorieViewSet, basename='categorie')
router.register(r'api/panier', PanierViewSet, basename='panier')

# Vue racine API – on évite les reverse sur noms internes Djoser
@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'produits': request.build_absolute_uri('/api/produits/'),
        'catégories': request.build_absolute_uri('/api/categories/'),
        'panier': request.build_absolute_uri('/api/panier/'),
        'inscription': request.build_absolute_uri('/api/auth/users/'),
        'connexion (JWT)': request.build_absolute_uri('/api/auth/jwt/create/'),
        # 'connexion (JWT)': 'POST /api/auth/jwt/create/',
        'rafraîchir token': request.build_absolute_uri('/api/auth/jwt/refresh/'),
        'profil & suppression compte': request.build_absolute_uri('/api/auth/users/me/'),
        'demander reset mot de passe': request.build_absolute_uri('/api/auth/users/reset_password/'),
        'confirmer reset mot de passe': request.build_absolute_uri('/api/auth/users/reset_password_confirm/'),
    })

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Racine API belle et stable
    path('', api_root, name='api-root'),

    # Routes automatiques du router
    path('', include(router.urls)),

    # Djoser – Auth complète
    path('api/auth/', include('djoser.urls')),          # reset password, activation, etc.
    path('api/auth/', include('djoser.urls.jwt')),      # JWT login, refresh, verify
]

