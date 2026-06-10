from rest_framework import generics, permissions, viewsets, mixins
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Profil, Bildirishnoma
from .serializers import (
    ProfilSerializer, BildirishnomaSerializer, RegisterSerializer, UserSerializer,
)


class RegisterAPI(generics.CreateAPIView):
    """Ro'yxatdan o'tish — token qaytaradi."""
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': UserSerializer(user).data}, status=201)


class LoginAPI(ObtainAuthToken):
    """Kirish — username/password yuboring, token oling."""
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        ser = self.serializer_class(data=request.data, context={'request': request})
        ser.is_valid(raise_exception=True)
        user = ser.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': UserSerializer(user).data})


class MeAPI(generics.RetrieveAPIView):
    """Joriy foydalanuvchi ma'lumotlari."""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ProfilMeAPI(generics.RetrieveUpdateAPIView):
    """O'z profilini ko'rish/tahrirlash."""
    serializer_class = ProfilSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profil, _ = Profil.objects.get_or_create(user=self.request.user)
        return profil


class BildirishnomaViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Bildirishnomalar ro'yxati va 'oqildi' deb belgilash."""
    serializer_class = BildirishnomaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.bildirishnomalar.all()

    @action(detail=False, methods=['post'])
    def oqildi(self, request):
        request.user.bildirishnomalar.filter(oqilgan=False).update(oqilgan=True)
        return Response({'status': 'ok'})
