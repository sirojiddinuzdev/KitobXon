from django.shortcuts import render,redirect
from .models import Kitob,Almashitirish
from django.contrib.auth.decorators import login_required
from .forms import KitobForm
# Create your views here.

def kitoblar_royhati(request):
    kitoblar = Kitob.objects.all()
    context = {
        'kitoblar':kitoblar
    }
    return render(request, 'books/kitoblar.html',context)

@login_required
def kitob_qoshish(request):
    if request.method == 'POST':
        form = KitobForm(request.POST, request.FILES)
        if form.is_valid:
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
