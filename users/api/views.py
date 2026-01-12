from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    CustomTokenObtainPairSerializer,
    RegisterSerializer,
    UserSerializer
)
from ..models import Utilisateur


class CustomTokenObtainTokenPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.user
        token = serializer.validated_data

        # 🔥 Plus de vérification du statut : tout le monde est APPROVED
        return Response({
            'refresh': str(token['refresh']),
            'access': str(token['access']),
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)


class RegisterView(generics.CreateAPIView):
    queryset = Utilisateur.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer


class ProfileView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user