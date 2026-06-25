from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count
from django.urls import reverse

from .models import Kitob, Almashitirish, Sevimli, Sharh, Istak
from .forms import KitobForm, IstakForm
from .tasks import sorov_qabul_email
from accounts.utils import bildir

# Create your views here.
# REST API endi books/api.py va config/urls.py da (DRF router).


def kitoblar_royhati(request):
    kitoblar = (
        Kitob.objects.filter(mavjud=True)
        .select_related('ega')
        .annotate(avg_baho=Avg('sharhlar__baho'), sharh_soni=Count('sharhlar', distinct=True))
        .order_by('-yaratildi')
    )

    qidiruv = request.GET.get('q')
    if qidiruv:
        kitoblar = kitoblar.filter(
            Q(nomi__icontains=qidiruv) | Q(muallif__icontains=qidiruv)
        )

    janr = request.GET.get('janr')
    if janr:
        kitoblar = kitoblar.filter(janr=janr)

    hudud = request.GET.get('hudud')
    if hudud:
        kitoblar = kitoblar.filter(hudud=hudud)

    # Pagination
    paginator = Paginator(kitoblar, 6)
    sahifa = request.GET.get('sahifa')
    kitoblar_sahifa = paginator.get_page(sahifa)

    # Filter parametrlarini saqlash uchun (pagination linklarida)
    get_params = request.GET.copy()
    get_params.pop('sahifa', None)
    querystring = get_params.urlencode()

    yuborilgan_kitob_idlar = []
    sevimli_idlar = []
    if request.user.is_authenticated:
        yuborilgan_kitob_idlar = list(
            Almashitirish.objects.filter(yuboruvchi=request.user)
            .values_list('kitob_id', flat=True)
        )
        sevimli_idlar = list(
            Sevimli.objects.filter(foydalanuvchi=request.user)
            .values_list('kitob_id', flat=True)
        )

    context = {
        'kitoblar': kitoblar_sahifa,
        'jami': paginator.count,
        'qidiruv': qidiruv,
        'janr': janr,
        'hudud': hudud,
        'querystring': querystring,
        'yuborilgan_kitob_idlar': yuborilgan_kitob_idlar,
        'sevimli_idlar': sevimli_idlar,
        'janr_tanlov': Kitob.Janr_Tanlov,
        'hudud_tanlov': Kitob.Hudud_tanlov,
    }
    return render(request, 'books/kitoblar.html', context)


def kitob_detail(request, kitob_id):
    kitob = get_object_or_404(Kitob.objects.select_related('ega'), id=kitob_id)
    sharhlar = kitob.sharhlar.select_related('muallif')

    # Sharh qoldirish (faqat tizimga kirgan, kitob egasi bo'lmagan foydalanuvchi)
    if request.method == 'POST' and request.user.is_authenticated and request.user != kitob.ega:
        try:
            baho = int(request.POST.get('baho', 0))
        except (TypeError, ValueError):
            baho = 0
        matn = request.POST.get('matn', '').strip()
        if 1 <= baho <= 5:
            _, yangi = Sharh.objects.update_or_create(
                kitob=kitob, muallif=request.user,
                defaults={'baho': baho, 'matn': matn},
            )
            bildir(
                kitob.ega,
                f'{request.user.username} "{kitob.nomi}" kitobiga sharh qoldirdi',
                reverse('kitob-detail', args=[kitob.id]),
                'info',
            )
            messages.success(request, 'Sharhingiz saqlandi.')
        else:
            messages.error(request, 'Iltimos, 1 dan 5 gacha baho tanlang.')
        return redirect('kitob-detail', kitob_id=kitob.id)

    agg = sharhlar.aggregate(ortacha=Avg('baho'), soni=Count('id'))
    ortacha_baho = round(agg['ortacha'], 1) if agg['ortacha'] else 0
    sharh_soni = agg['soni']

    sorov_yuborilgan = False
    sevimli = False
    foydalanuvchi_sharhi = None
    taklif_kitoblar = []
    if request.user.is_authenticated:
        sorov_yuborilgan = Almashitirish.objects.filter(
            kitob=kitob, yuboruvchi=request.user
        ).exists()
        sevimli = Sevimli.objects.filter(
            foydalanuvchi=request.user, kitob=kitob
        ).exists()
        foydalanuvchi_sharhi = sharhlar.filter(muallif=request.user).first()
        if request.user != kitob.ega:
            taklif_kitoblar = request.user.books.filter(mavjud=True)

    oxshash = (
        Kitob.objects.filter(janr=kitob.janr, mavjud=True)
        .exclude(id=kitob.id)
        .select_related('ega')[:3]
    )

    context = {
        'kitob': kitob,
        'sorov_yuborilgan': sorov_yuborilgan,
        'sevimli': sevimli,
        'oxshash': oxshash,
        'sharhlar': sharhlar,
        'ortacha_baho': ortacha_baho,
        'sharh_soni': sharh_soni,
        'foydalanuvchi_sharhi': foydalanuvchi_sharhi,
        'taklif_kitoblar': taklif_kitoblar,
    }
    return render(request, 'books/kitob_detail.html', context)


@login_required
def kitob_qoshish(request):
    if request.method == 'POST':
        form = KitobForm(request.POST, request.FILES)
        if form.is_valid():
            kitob = form.save(commit=False)
            kitob.ega = request.user
            kitob.save()
            _istak_mosligini_tekshir(kitob)
            messages.success(request, 'Kitob muvaffaqiyatli qo‘shildi.')
            return redirect('profil')
    else:
        form = KitobForm()
    return render(request, 'books/kitob_qoshish.html', {'form': form})


@login_required
def kitob_tahrirlash(request, kitob_id):
    kitob = get_object_or_404(Kitob, id=kitob_id, ega=request.user)
    if request.method == 'POST':
        form = KitobForm(request.POST, request.FILES, instance=kitob)
        if form.is_valid():
            form.save()
            messages.success(request, 'Kitob muvaffaqiyatli yangilandi.')
            return redirect('profil')
    else:
        form = KitobForm(instance=kitob)
    return render(request, 'books/kitob_qoshish.html', {'form': form, 'tahrirlash': True, 'kitob': kitob})


@login_required
def kitob_ochirish(request, kitob_id):
    kitob = get_object_or_404(Kitob, id=kitob_id, ega=request.user)
    if request.method == 'POST':
        kitob.delete()
        messages.success(request, 'Kitob o‘chirildi.')
        return redirect('profil')
    return render(request, 'books/kitob_ochirish.html', {'kitob': kitob})


def _istak_mosligini_tekshir(yangi_kitob):
    """Yangi kitob kimningdir wishlist'iga mos kelsa, egasiga bildirishnoma."""
    nomi = yangi_kitob.nomi.lower()
    istaklar = Istak.objects.filter(topildi=False).exclude(foydalanuvchi=yangi_kitob.ega)
    for istak in istaklar:
        iv = istak.nomi.lower().strip()
        if iv and (iv in nomi or nomi in iv):
            bildir(
                istak.foydalanuvchi,
                f'Siz izlagan "{istak.nomi}" kitobi qo‘shildi: "{yangi_kitob.nomi}"',
                reverse('kitob-detail', args=[yangi_kitob.id]),
                'success',
            )
            istak.topildi = True
            istak.save(update_fields=['topildi'])


@login_required
def sorov_yuborish(request, kitob_id):
    kitob = get_object_or_404(Kitob, id=kitob_id)

    if kitob.ega == request.user:
        messages.warning(request, 'Bu sizning kitobingiz.')
        return redirect('kitoblar-royhati')

    if not kitob.mavjud:
        messages.warning(request, 'Bu kitob hozircha band.')
        return redirect('kitoblar-royhati')

    # Teskari taklif (ixtiyoriy): foydalanuvchi o'z kitobini almashtirishga taklif qiladi
    taklif = None
    taklif_id = request.POST.get('taklif_kitob') or request.GET.get('taklif_kitob')
    if taklif_id:
        taklif = Kitob.objects.filter(id=taklif_id, ega=request.user, mavjud=True).first()

    sorov, yaratildi = Almashitirish.objects.get_or_create(
        kitob=kitob, yuboruvchi=request.user,
        defaults={'taklif_kitob': taklif},
    )
    if yaratildi:
        matn = f'{request.user.username} "{kitob.nomi}" kitobingizga so‘rov yubordi'
        if taklif:
            matn += f' (almashtirishga: "{taklif.nomi}")'
        bildir(kitob.ega, matn, reverse('profil'), 'info')
        messages.success(request, f'"{kitob.nomi}" uchun so‘rov yuborildi.')
    else:
        messages.info(request, 'Siz allaqachon so‘rov yuborgansiz.')

    return redirect(request.POST.get('next') or request.GET.get('next') or 'kitoblar-royhati')


@login_required
def istaklar(request):
    """Wishlist: izlanayotgan kitoblarni qo'shish/ko'rish."""
    if request.method == 'POST':
        form = IstakForm(request.POST)
        if form.is_valid():
            istak = form.save(commit=False)
            istak.foydalanuvchi = request.user
            istak.save()
            messages.success(request, 'Izlanayotgan kitob qo‘shildi.')
            return redirect('istaklar')
    else:
        form = IstakForm()
    mening_istaklarim = request.user.istaklar.all()
    return render(request, 'books/istaklar.html', {'form': form, 'istaklar': mening_istaklarim})


@login_required
def istak_ochirish(request, istak_id):
    istak = get_object_or_404(Istak, id=istak_id, foydalanuvchi=request.user)
    istak.delete()
    messages.success(request, 'O‘chirildi.')
    return redirect('istaklar')


def izlanayotgan(request):
    """Hammaga ochiq: foydalanuvchilar izlayotgan kitoblar ro'yxati."""
    qidiruv = request.GET.get('q')
    qs = Istak.objects.filter(topildi=False).select_related('foydalanuvchi')
    if qidiruv:
        qs = qs.filter(nomi__icontains=qidiruv)
    return render(request, 'books/izlanayotgan.html', {'istaklar': qs, 'qidiruv': qidiruv})


@login_required
def tarix(request):
    """Almashinuv tarixi/arxivi: hal qilingan (qabul/rad) so'rovlar."""
    kelgan = Almashitirish.objects.filter(
        kitob__ega=request.user, holat__in=['qabul', 'rad']
    ).select_related('kitob', 'yuboruvchi', 'taklif_kitob')
    yuborilgan = Almashitirish.objects.filter(
        yuboruvchi=request.user, holat__in=['qabul', 'rad']
    ).select_related('kitob', 'kitob__ega', 'taklif_kitob')
    return render(request, 'books/tarix.html', {'kelgan': kelgan, 'yuborilgan': yuborilgan})


@login_required
def sevimli_toggle(request, kitob_id):
    kitob = get_object_or_404(Kitob, id=kitob_id)
    sevimli, yaratildi = Sevimli.objects.get_or_create(
        foydalanuvchi=request.user, kitob=kitob
    )
    if not yaratildi:
        sevimli.delete()
        messages.info(request, f'"{kitob.nomi}" sevimlilardan olib tashlandi.')
    else:
        messages.success(request, f'"{kitob.nomi}" sevimlilarga qo‘shildi.')
    return redirect(request.GET.get('next') or 'kitoblar-royhati')


@login_required
def sevimlilar(request):
    sevimli_kitoblar = (
        Kitob.objects.filter(sevib_qolinganlar__foydalanuvchi=request.user)
        .select_related('ega')
        .order_by('-sevib_qolinganlar__yaratildi')
    )
    return render(request, 'books/sevimlilar.html', {'kitoblar': sevimli_kitoblar})


@login_required
def sorov_qabul(request, sorov_id):
    sorov = get_object_or_404(Almashitirish, id=sorov_id)

    if sorov.kitob.ega == request.user:
        sorov.holat = "qabul"
        sorov.save()

        sorov.kitob.mavjud = False
        sorov.kitob.save()
        if sorov.yuboruvchi.email:
            sorov_qabul_email.delay(
                yuboruvchi_email=sorov.yuboruvchi.email,
                kitob_nomi=sorov.kitob.nomi,
                ega_username=request.user.username,
            )

        bildir(
            sorov.yuboruvchi,
            f'"{sorov.kitob.nomi}" uchun so‘rovingiz qabul qilindi! Egasi bilan bog‘laning.',
            reverse('profil'),
            'success',
        )
        messages.success(request, f"{sorov.yuboruvchi.username} ning so‘rovi qabul qilindi")

    return redirect('profil')


@login_required
def sorov_rad(request, sorov_id):
    sorov = get_object_or_404(Almashitirish, id=sorov_id)

    if sorov.kitob.ega == request.user:
        sorov.holat = 'rad'
        sorov.save()
        bildir(
            sorov.yuboruvchi,
            f'"{sorov.kitob.nomi}" uchun so‘rovingiz rad etildi',
            reverse('profil'),
            'warning',
        )
        messages.warning(request, f"{sorov.yuboruvchi.username} ning so‘rovi rad etildi")

    return redirect('profil')
