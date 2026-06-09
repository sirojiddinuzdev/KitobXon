from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from books.models import Almashitirish
from .models import Profil
from .forms import ProfilForm, RegisterForm, LoginForm

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


def _aktivlashtirish_email_yuborish(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    link = request.build_absolute_uri(reverse('activate', args=[uid, token]))
    matn = render_to_string('accounts/activation_email.html', {
        'user': user, 'link': link,
    })
    send_mail(
        'KitobXon — Emailingizni tasdiqlang',
        matn,
        None,
        [user.email],
        fail_silently=False,
    )


def royhatdan_otish(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # email tasdiqlangunicha nofaol
            user.save()
            Profil.objects.create(user=user)
            _aktivlashtirish_email_yuborish(request, user)
            return render(request, 'accounts/activation_sent.html', {'email': user.email})
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {"form": form})


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, 'Email tasdiqlandi! KitobXon\'ga xush kelibsiz.')
        return redirect('kitoblar-royhati')

    return render(request, 'accounts/activation_invalid.html')

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

