from django.shortcuts import render,redirect
from .models import Kitob,Almashitirish
from django.contrib.auth.decorators import login_required
from .forms import KitobForm
# Create your views here.

def kitoblar_royhati(request):
    kitoblar = Kitob.objects.all()


    qidiruv = request.GET.get('q')
    if qidiruv:
        kitoblar = kitoblar.filter(nomi__icontains = qidiruv) | kitoblar.filter(muallif__icontains = qidiruv)
    janr = request.GET.get('janr')
    if janr:
        kitoblar = kitoblar.filter(janr=janr)

    context = {
        'kitoblar':kitoblar,
        'qidiruv':qidiruv,
        'janr':janr
        
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
    kitob = Kitob.objects.get(id=kitob_id)
    if kitob.ega==request.user:
        return redirect('kitoblar-royhati')
    mavjud_sorov = Almashitirish.objects.filter(kitob=kitob,yuboruvchi=request.user).exists()
    if not mavjud_sorov:
        Almashitirish.objects.create(kitob=kitob,yuboruvchi=request.user)

    return redirect('kitoblar-royhati')

@login_required
def sorov_qabul(request,sorov_id):
    sorov = Almashitirish.objects.get(id=sorov_id)

    if sorov.kitob.ega == request.user:
        sorov.holat = "qabul"
        sorov.save()

        sorov.kitob.mavjud = False
        sorov.kitob.save()
    return redirect('profil')

@login_required
def sorov_rad(request,sorov_id):
    sorov = Almashitirish.objects.get(id=sorov_id)

    if sorov.kitob.ega==request.user:
        sorov.holat = 'rad'
        sorov.save()
        return redirect('profil')