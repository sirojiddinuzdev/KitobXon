from django.shortcuts import render,redirect
from .models import Kitob,Almashitirish
from django.contrib.auth.decorators import login_required
from .forms import KitobForm
from django.shortcuts import get_object_or_404
from django.contrib import messages
from .tasks import sorov_qabul_email

from rest_framework import generics, permissions
from .serializers import KitobSerializer, AlmashitirishSerializer

# Create your views here.

def kitoblar_royhati(request):
    kitoblar = Kitob.objects.all()
    qidiruv = request.GET.get('q')
    if qidiruv:
        kitoblar = kitoblar.filter(nomi__icontains = qidiruv) | kitoblar.filter(muallif__icontains = qidiruv)
    janr = request.GET.get('janr')
    if janr:
        kitoblar = kitoblar.filter(janr=janr)
    yuborilgan_kitob_idlar = []

    hudud = request.GET.get('hudud')
    if hudud:
        kitoblar = kitoblar.filter(hudud=hudud)
    if request.user.is_authenticated:
        yuborilgan_kitob_idlar = Almashitirish.objects.filter(
            yuboruvchi=request.user
        ).values_list('kitob_id', flat=True)
    context = {
        'kitoblar':kitoblar,
        'qidiruv':qidiruv,
        'janr':janr,
        'yuborilgan_kitob_idlar':yuborilgan_kitob_idlar
    }
    return render(request, 'books/kitoblar.html',context)

@login_required
def kitob_qoshish(request):
    if request.method == 'POST':
        form = KitobForm(request.POST, request.FILES)
        if form.is_valid():
            kitob = form.save(commit=False)
            kitob.ega = request.user
            kitob.save()
            return redirect('profil')
    else:
        form = KitobForm()
    return render(request, 'books/kitob_qoshish.html', {'form':form})

@login_required
def sorov_yuborish(request,kitob_id):
    kitob = get_object_or_404(Kitob,id=kitob_id)

    if kitob.ega==request.user:
        return redirect('kitoblar-royhati')
    if kitob.ega==request.user:
        return redirect('kitoblar-royhati')
    mavjud_sorov = Almashitirish.objects.filter(kitob=kitob,yuboruvchi=request.user).exists()

    if not mavjud_sorov:
        Almashitirish.objects.create(kitob=kitob,yuboruvchi=request.user)

    return redirect('kitoblar-royhati')

@login_required
def sorov_qabul(request,sorov_id):
    sorov = get_object_or_404(Almashitirish,id=sorov_id)

    if sorov.kitob.ega == request.user:
        sorov.holat = "qabul"
        sorov.save()

        sorov.kitob.mavjud = False
        sorov.kitob.save()
        if sorov.yuboruvchi.email:
            sorov_qabul_email.delay(
                yuboruvchi_email=sorov.yuboruvchi.email,
                kitob_nomi = sorov.kitob.nomi,
                ega_username = request.user.username)

        messages.success(request,f"{sorov.yuboruvchi.username} ning sorovi qabul qilindi")
        
    return redirect('profil')

@login_required
def sorov_rad(request,sorov_id):
    sorov = Almashitirish.objects.get(id=sorov_id)

    if sorov.kitob.ega==request.user:
        sorov.holat = 'rad'
        sorov.save()
        messages.warning(request,f"{sorov.yuboruvchi.username} ning sorovi rad etildi")
        
    return redirect('profil')
##################################################################

class KitobListAPI(generics.ListAPIView):
    queryset = Kitob.objects.all()
    serializer_class = KitobSerializer
    permission_classes = [permissions.AllowAny]

class KitobDetailAPI(generics.RetrieveAPIView):
    queryset = Kitob.objects.all()
    serializer_class = KitobSerializer
    permission_classes = [permissions.AllowAny]

class MeningKitoblarimAPI(generics.ListAPIView):
    serializer_class = KitobSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Kitob.objects.filter(ega=self.request.user)

class AlmashitirishListAPI(generics.ListAPIView):
    serializer_class = AlmashitirishSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Almashitirish.objects.filter(yuboruvchi=self.request.user)
##################################################################