from django.db.models import Q, Avg, Count
from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Kitob, Almashitirish, Sevimli, Sharh
from .serializers import (
    KitobSerializer, AlmashitirishSerializer, SevimliSerializer, SharhSerializer,
)
from accounts.utils import bildir


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Yozish faqat egasiga; o'qish hammaga."""
    message = "Bu amalni faqat egasi bajara oladi."

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        ega = getattr(obj, 'ega', None) or getattr(obj, 'foydalanuvchi', None)
        return ega == request.user


class KitobViewSet(viewsets.ModelViewSet):
    """Kitoblar: ro'yxat, qidiruv/filter, batafsil, qo'shish, tahrir, o'chirish (egasi)."""
    serializer_class = KitobSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        qs = (
            Kitob.objects.select_related('ega')
            .annotate(avg_baho=Avg('sharhlar__baho'),
                      sharh_soni_ann=Count('sharhlar', distinct=True))
        )
        p = self.request.query_params
        if p.get('mine') in ('1', 'true', 'True') and self.request.user.is_authenticated:
            qs = qs.filter(ega=self.request.user)
        q = p.get('q')
        if q:
            qs = qs.filter(Q(nomi__icontains=q) | Q(muallif__icontains=q))
        if p.get('janr'):
            qs = qs.filter(janr=p['janr'])
        if p.get('hudud'):
            qs = qs.filter(hudud=p['hudud'])
        if p.get('mavjud') in ('1', 'true', 'True'):
            qs = qs.filter(mavjud=True)
        return qs.order_by('-yaratildi')

    def perform_create(self, serializer):
        serializer.save(ega=self.request.user)

    @action(detail=True, methods=['get'])
    def sharhlar(self, request, pk=None):
        kitob = self.get_object()
        ser = SharhSerializer(kitob.sharhlar.select_related('muallif'), many=True)
        return Response(ser.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def sharh(self, request, pk=None):
        kitob = self.get_object()
        if kitob.ega == request.user:
            return Response({'detail': "O'z kitobingizga sharh qoldira olmaysiz."},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            baho = int(request.data.get('baho'))
        except (TypeError, ValueError):
            baho = 0
        if not 1 <= baho <= 5:
            return Response({'detail': 'baho 1 dan 5 gacha bo‘lsin.'},
                            status=status.HTTP_400_BAD_REQUEST)
        matn = request.data.get('matn', '')
        obj, _ = Sharh.objects.update_or_create(
            kitob=kitob, muallif=request.user, defaults={'baho': baho, 'matn': matn})
        bildir(kitob.ega, f'{request.user.username} "{kitob.nomi}" kitobiga sharh qoldirdi', '', 'info')
        return Response(SharhSerializer(obj).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def sevimli(self, request, pk=None):
        kitob = self.get_object()
        obj, created = Sevimli.objects.get_or_create(foydalanuvchi=request.user, kitob=kitob)
        if not created:
            obj.delete()
            return Response({'sevimli': False})
        return Response({'sevimli': True}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def sorov(self, request, pk=None):
        kitob = self.get_object()
        if kitob.ega == request.user:
            return Response({'detail': 'Bu sizning kitobingiz.'}, status=status.HTTP_400_BAD_REQUEST)
        if not kitob.mavjud:
            return Response({'detail': 'Kitob band.'}, status=status.HTTP_400_BAD_REQUEST)
        sorov, created = Almashitirish.objects.get_or_create(kitob=kitob, yuboruvchi=request.user)
        if created:
            bildir(kitob.ega, f'{request.user.username} "{kitob.nomi}" kitobingizga so‘rov yubordi', '', 'info')
        return Response(
            AlmashitirishSerializer(sorov, context={'request': request}).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class SevimliListAPI(generics.ListAPIView):
    """Foydalanuvchining sevimli kitoblari."""
    serializer_class = SevimliSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Sevimli.objects.filter(foydalanuvchi=self.request.user)
            .select_related('kitob', 'kitob__ega')
        )


class SorovViewSet(viewsets.ReadOnlyModelViewSet):
    """Almashtirish so'rovlari: ro'yxat (?turi=kelgan|yuborilgan), qabul/rad (egasi)."""
    serializer_class = AlmashitirishSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        u = self.request.user
        turi = self.request.query_params.get('turi')
        base = Almashitirish.objects.select_related('kitob', 'kitob__ega', 'yuboruvchi')
        if turi == 'kelgan':
            return base.filter(kitob__ega=u)
        if turi == 'yuborilgan':
            return base.filter(yuboruvchi=u)
        return base.filter(Q(yuboruvchi=u) | Q(kitob__ega=u))

    @action(detail=True, methods=['post'])
    def qabul(self, request, pk=None):
        sorov = self.get_object()
        if sorov.kitob.ega != request.user:
            return Response({'detail': 'Faqat kitob egasi qabul qila oladi.'}, status=status.HTTP_403_FORBIDDEN)
        sorov.holat = 'qabul'
        sorov.save()
        sorov.kitob.mavjud = False
        sorov.kitob.save()
        bildir(sorov.yuboruvchi, f'"{sorov.kitob.nomi}" uchun so‘rovingiz qabul qilindi', '', 'success')
        return Response(AlmashitirishSerializer(sorov, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def rad(self, request, pk=None):
        sorov = self.get_object()
        if sorov.kitob.ega != request.user:
            return Response({'detail': 'Faqat kitob egasi rad eta oladi.'}, status=status.HTTP_403_FORBIDDEN)
        sorov.holat = 'rad'
        sorov.save()
        bildir(sorov.yuboruvchi, f'"{sorov.kitob.nomi}" uchun so‘rovingiz rad etildi', '', 'warning')
        return Response(AlmashitirishSerializer(sorov, context={'request': request}).data)
