from django.shortcuts import render,redirect
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from books.models import Almashitirish
from .models import Profil
from .forms import ProfilForm, RegisterForm

# Create your views here.

@login_required
def profil(request):
    profil,_ = Profil.objects.get_or_create(user = request.user)
    # form = None
    if request.method == "POST":
        form = ProfilForm(request.POST,instance=profil)
        if form.is_valid():
            form.save()
            return redirect('profil')
    else:
            form = ProfilForm(instance=profil)
        
    mening_kitoblarim = request.user.books.all()

    kelgan_sorovlar = Almashitirish.objects.filter(
        kitob__ega = request.user
    )
    yuborilgan_sorovlar = Almashitirish.objects.filter(yuboruvchi=request.user)

    for sorov in yuborilgan_sorovlar:
        try:
            sorov.ega_profil = Profil.objects.get(user=sorov.kitob.ega)
        except Profil.DoesNotExist:
            sorov.ega_profil = None
    context = {
        'mening_kitoblarim':mening_kitoblarim,
        'kelgan_sorovlar':kelgan_sorovlar,
        'yuborilgan_sorovlar':yuborilgan_sorovlar,
        'form':form,
        'profil':profil
    }
    return render(request,'accounts/profil.html',context)

def royhatdan_otish(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profil.objects.create(user=user)
            login(request,user)
            return redirect('kitoblar-royhati')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {"form": form})

def kirish(request):
    if request.method == 'POST':
        form = AuthenticationForm(data = request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request,user)
            return redirect('kitoblar-royhati')
    else:
        form = AuthenticationForm()
    return render(request,'accounts/login.html',{'form':form})
        
def chiqish(request):
    logout(request)
    return redirect('kirish')

