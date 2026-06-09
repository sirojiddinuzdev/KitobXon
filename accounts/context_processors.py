from books.models import Almashitirish


def navbar_context(request):
    """Navbar uchun umumiy ma'lumotlar: kutilayotgan so'rovlar soni va profil."""
    if not request.user.is_authenticated:
        return {}

    kutilayotgan_sorovlar = Almashitirish.objects.filter(
        kitob__ega=request.user, holat='kutilmoqda'
    ).count()

    profil = getattr(request.user, 'profil', None)

    return {
        'kutilayotgan_sorovlar': kutilayotgan_sorovlar,
        'nav_profil': profil,
    }
