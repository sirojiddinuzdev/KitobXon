import logging
import secrets
from datetime import timedelta
from django.db import transaction
from django.utils import timezone
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from .models import Profil, TasdiqlashKodi

User = get_user_model()
logger = logging.getLogger(__name__)


def royxatdan_otish_service(username, email, password):
    """
    Foydalanuvchini atomik ro'yxatdan o'tkazish.
    Agar send_mail SMTP xatoligi bersa, tranzaksiya avtomatik ROLLBACK bo'ladi va DB da chala user qolmaydi.
    """
    with transaction.atomic():
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_active=False
        )
        Profil.objects.get_or_create(user=user)

        # Kriptografik xavfsiz 6-xonali kod
        kod = f"{secrets.randbelow(1000000):06d}"
        tasdiqlash_kodi = TasdiqlashKodi.objects.create(user=user, kod=kod)

        try:
            send_mail(
                subject='KitobXon — Tasdiqlash kodi',
                message=f'Sizning tasdiqlash kodingiz: {kod}',
                from_email='kitobxon@gmail.com',
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception as e:
            # Exception tashlash transaction.atomic ni ROLLBACK qiladi
            logger.error(
                "royxatdan_otish_service: SMTP xatosi, foydalanuvchi rollback qilindi | email=%s | xato=%s",
                email, e,
            )
            raise ValidationError("Email yuborishda xatolik yuz berdi. Iltimos qayta urining.") from e

    return user, tasdiqlash_kodi


def tasdiqlash_kodi_tekshirish_service(user_id, kod):
    """
    Tasdiqlash kodini atomik tekshirish va aktivlashtirish (Replay va Race condition himoyasi).
    """
    with transaction.atomic():
        try:
            tasdiqlash_kodi = TasdiqlashKodi.objects.select_for_update().get(
                user_id=user_id,
                tasdiqlangan=False
            )
        except TasdiqlashKodi.DoesNotExist:
            raise ValidationError("Faol tasdiqlash kodi topilmadi.")

        if tasdiqlash_kodi.urinishlar_soni >= 5:
            logger.warning(
                "tasdiqlash_kodi_tekshirish: urinishlar chekidan oshdi | user_id=%s",
                user_id,
            )
            raise ValidationError("Urinishlar soni cheklovdan oshdi. Qayta ro'yxatdan o'ting.")

        if timezone.now() > tasdiqlash_kodi.yaratildi + timedelta(minutes=10):
            logger.warning(
                "tasdiqlash_kodi_tekshirish: muddati tugagan OTP ishlatilmoqda | user_id=%s",
                user_id,
            )
            raise ValidationError("Kodning yaroqlilik muddati (10 daqiqa) tugagan.")

        if tasdiqlash_kodi.kod != str(kod).strip():
            tasdiqlash_kodi.urinishlar_soni += 1
            tasdiqlash_kodi.save(update_fields=['urinishlar_soni'])
            code_matched = False
        else:
            code_matched = True
            tasdiqlash_kodi.tasdiqlangan = True
            tasdiqlash_kodi.save(update_fields=['tasdiqlangan'])

            user = tasdiqlash_kodi.user
            user.is_active = True
            user.save(update_fields=['is_active'])

    if not code_matched:
        raise ValidationError(f"Kod noto'g'ri! Qolgan urinishlar: {5 - tasdiqlash_kodi.urinishlar_soni}")

    return user, tasdiqlash_kodi
