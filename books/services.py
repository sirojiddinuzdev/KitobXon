from django.db import transaction
from django.core.exceptions import ValidationError
from django.urls import reverse

from .models import Kitob, Almashitirish
from .tasks import sorov_qabul_email
from accounts.utils import bildir

# Qulaylik uchun alias
Holat = Almashitirish.Holat


def qabul_qilish_service(sorov_id, user):
    """
    Almashtirish so'rovini atomik tarzda qabul qilish.
    Holat qoidalari: Almashitirish.Holat (yagona manba).
    """
    with transaction.atomic():
        try:
            sorov = Almashitirish.objects.select_for_update().get(id=sorov_id)
        except Almashitirish.DoesNotExist:
            raise ValidationError("So'rov topilmadi.")

        if sorov.kitob.ega != user:
            raise ValidationError("Faqat kitob egasi so'rovni qabul qila oladi.")

        if not sorov.kutilmoqdami():
            raise ValidationError("Faqat kutilayotgan so'rovlarni qabul qilish mumkin.")

        kitob = Kitob.objects.select_for_update().get(id=sorov.kitob_id)
        if not kitob.mavjud:
            raise ValidationError("Bu kitob allaqachon boshqa kishiga berilgan.")

        sorov.holat = Holat.QABUL
        sorov.save()

        kitob.mavjud = False
        kitob.save()

        # Boshqa kutilayotgan so'rovlarni rad etamiz
        Almashitirish.objects.filter(
            kitob=kitob, holat=Holat.KUTILMOQDA
        ).exclude(id=sorov.id).update(holat=Holat.RAD)

    # Tranzaksiyadan so'ng bildirishnoma va email yuborish
    if sorov.yuboruvchi.email:
        try:
            sorov_qabul_email.delay(
                yuboruvchi_email=sorov.yuboruvchi.email,
                kitob_nomi=sorov.kitob.nomi,
                ega_username=user.username,
            )
        except Exception:
            pass

    bildir(
        sorov.yuboruvchi,
        f'"{sorov.kitob.nomi}" uchun so\'rovingiz qabul qilindi! Egasi bilan bog\'laning.',
        reverse('profil'),
        'success',
    )
    return sorov


def rad_etish_service(sorov_id, user):
    """
    Almashtirish so'rovini atomik tarzda rad etish.
    Holat qoidalari: Almashitirish.Holat (yagona manba).
    """
    with transaction.atomic():
        try:
            sorov = Almashitirish.objects.select_for_update().get(id=sorov_id)
        except Almashitirish.DoesNotExist:
            raise ValidationError("So'rov topilmadi.")

        if sorov.kitob.ega != user:
            raise ValidationError("Faqat kitob egasi so'rovni rad eta oladi.")

        if not sorov.kutilmoqdami():
            raise ValidationError("Faqat kutilayotgan so'rovlarni rad etish mumkin.")

        sorov.holat = Holat.RAD
        sorov.save()

    bildir(
        sorov.yuboruvchi,
        f'"{sorov.kitob.nomi}" uchun so\'rovingiz rad etildi',
        reverse('profil'),
        'warning',
    )
    return sorov
