from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta

from books.models import Almashitirish
from .models import Profil,TasdiqlashKodi
from .forms import ProfilForm, RegisterForm, LoginForm,TasdiqlashForm,RoyxatForm
from .services import royxatdan_otish_service, tasdiqlash_kodi_tekshirish_service
from django.core.exceptions import ValidationError
from django.core.mail import send_mail

# Create your views here.

@login_required
def profil(request):
    profil, _ = Profil.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = ProfilForm(request.POST, request.FILES, instance=profil)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil yangilandi.')
            return redirect('profil')
    else:
        form = ProfilForm(instance=profil)

    mening_kitoblarim = request.user.books.all()

    kelgan_sorovlar = Almashitirish.objects.filter(
        kitob__ega=request.user
    ).select_related('kitob', 'yuboruvchi')
    yuborilgan_sorovlar = Almashitirish.objects.filter(
        yuboruvchi=request.user
    ).select_related('kitob', 'kitob__ega')

    for sorov in yuborilgan_sorovlar:
        try:
            sorov.ega_profil = Profil.objects.get(user=sorov.kitob.ega)
        except Profil.DoesNotExist:
            sorov.ega_profil = None

    # Statistika
    statistika = {
        'kitoblar': mening_kitoblarim.count(),
        'kelgan': kelgan_sorovlar.count(),
        'kutilayotgan': kelgan_sorovlar.filter(holat='kutilmoqda').count(),
        'sevimlilar': request.user.sevimlilar.count(),
    }

    context = {
        'mening_kitoblarim': mening_kitoblarim,
        'kelgan_sorovlar': kelgan_sorovlar,
        'yuborilgan_sorovlar': yuborilgan_sorovlar,
        'form': form,
        'profil': profil,
        'statistika': statistika,
    }
    return render(request, 'accounts/profil.html', context)

@login_required
def bildirishnomalar(request):
    qs = request.user.bildirishnomalar.all()
    items = list(qs[:50])
    # Ko'rilgach o'qilgan deb belgilaymiz
    qs.filter(oqilgan=False).update(oqilgan=True)
    return render(request, 'accounts/bildirishnomalar.html', {'bildirishnomalar': items})


def royhatdan_otish(request):
    if request.method == 'POST':
        form = RoyxatForm(request.POST)
        if form.is_valid():
            try:
                user, _ = royxatdan_otish_service(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password1']
                )
                request.session['tasdiqlash_user_id'] = user.id
                return redirect('tasdiqlash')
            except ValidationError as e:
                form.add_error(None, str(e.message if hasattr(e, 'message') else e))
    else:
        form = RoyxatForm()
    return render(request, 'accounts/register.html', {'form': form})


def kirish(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('kitoblar-royhati')
    else:
        form = LoginForm(request)
    return render(request, 'accounts/login.html', {'form': form})
        
def chiqish(request):
    logout(request)
    return redirect('kirish')

def tasdiqlash(request):
    user_id = request.session.get('tasdiqlash_user_id')
    if not user_id:
        return redirect('royxatdan-otish')

    if request.method == 'POST':
        form = TasdiqlashForm(request.POST)
        if form.is_valid():
            kod = form.cleaned_data['kod']
            try:
                user, _ = tasdiqlash_kodi_tekshirish_service(user_id, kod)
                login(request, user)
                return redirect('kitoblar-royhati')
            except ValidationError as e:
                return render(request, 'accounts/tasdiqlash.html', {
                    'form': form,
                    'xato': str(e.message if hasattr(e, 'message') else e)
                })
    else:
        form = TasdiqlashForm()
    return render(request, 'accounts/tasdiqlash.html', {'form': form})