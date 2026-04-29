from django.shortcuts import render,redirect
from .models import Kitob
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