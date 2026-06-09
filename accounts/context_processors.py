from books.models import Almashitirish
from .models import Bildirishnoma


def navbar_context(request):
    """Navbar uchun: kutilayotgan so'rovlar, o'qilmagan bildirishnomalar, profil."""
    if not request.user.is_authenticated:
        return {}

    kutilayotgan_sorovlar = Almashitirish.objects.filter(
        kitob__ega=request.user, holat='kutilmoqda'
    ).count()

    oqilmagan_bildirishnomalar = Bildirishnoma.objects.filter(
        foydalanuvchi=request.user, oqilgan=False
    ).count()

    profil = getattr(request.user, 'profil', None)

    return {
        'kutilayotgan_sorovlar': kutilayotgan_sorovlar,
        'oqilmagan_bildirishnomalar': oqilmagan_bildirishnomalar,
        'nav_profil': profil,
    }
