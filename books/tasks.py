import logging

from celery import shared_task
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,   # 60 soniyadan keyin qayta urinadi
    autoretry_for=(Exception,),
    retry_backoff=True,        # 60s → 120s → 240s (eksponentsial)
)
def sorov_qabul_email(self, yuboruvchi_email, kitob_nomi, ega_username):
    """
    So'rov qabul qilinganida xabarnoma emaili yuboradi.
    SMTP xatosi yuz bersa — 3 marta qayta urinadi (exponential backoff).
    Barcha urinishlar va xatolar 'books' loggeriga yoziladi.
    """
    logger.info(
        "sorov_qabul_email: yuborish boshlandi | kitob=%s | email=%s | urinish=%d/%d",
        kitob_nomi, yuboruvchi_email, self.request.retries + 1, self.max_retries + 1,
    )
    try:
        send_mail(
            subject="KitobXon — So'rovingiz qabul qilindi!",
            message=(
                f"Salom!\n\n"
                f'"{kitob_nomi}" kitobiga yuborgan so\'rovingiz qabul qilindi.\n\n'
                f"Kitob egasi {ega_username} bilan bog'laning.\n\n"
                f"KitobXon jamoasi"
            ),
            from_email='kitobxon@gmail.com',
            recipient_list=[yuboruvchi_email],
            fail_silently=False,
        )
        logger.info(
            "sorov_qabul_email: muvaffaqiyatli yuborildi | kitob=%s | email=%s",
            kitob_nomi, yuboruvchi_email,
        )
    except Exception as exc:
        logger.warning(
            "sorov_qabul_email: SMTP xatosi (urinish %d/%d) | kitob=%s | xato=%s",
            self.request.retries + 1, self.max_retries + 1,
            kitob_nomi, exc,
        )
        raise  # autoretry_for bu exceptionni tutib, qayta urinadi