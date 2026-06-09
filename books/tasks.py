from celery import shared_task
from django.core.mail import send_mail

@shared_task
def sorov_qabul_email(yuboruvchi_email, kitob_nomi, ega_username):
    send_mail(
        subject='KitobXon — So\'rovingiz qabul qilindi!',
        message=f'''
Salom!

"{kitob_nomi}" kitobiga yuborgan so\'rovingiz qabul qilindi.

Kitob egasi {ega_username} bilan bog\'laning.

KitobXon jamoasi
        ''',
        from_email=None,  # DEFAULT_FROM_EMAIL (noreply) ishlatiladi
        recipient_list=[yuboruvchi_email],
        fail_silently=False,
    )