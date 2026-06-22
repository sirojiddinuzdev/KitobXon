"""Mavjud (eski) rasmlarni qayta optimallashtirish.

Production'da allaqachon yuklangan katta rasmlarni bir martalik
kichraytirish uchun:

    python manage.py optimize_images
"""
from django.core.management.base import BaseCommand

from books.imaging import optimize_image_field
from books.models import Kitob
from accounts.models import Profil


class Command(BaseCommand):
    help = "Mavjud kitob muqovalari va avatarlarni kichraytirib qayta siqadi."

    def handle(self, *args, **options):
        kitob_soni = 0
        for kitob in Kitob.objects.exclude(rasm='').exclude(rasm__isnull=True):
            optimize_image_field(kitob.rasm, max_w=1000, max_h=1000)
            kitob_soni += 1

        avatar_soni = 0
        for profil in Profil.objects.exclude(avatar='').exclude(avatar__isnull=True):
            optimize_image_field(profil.avatar, max_w=400, max_h=400)
            avatar_soni += 1

        self.stdout.write(self.style.SUCCESS(
            f"Tayyor: {kitob_soni} ta muqova, {avatar_soni} ta avatar optimallashtirildi."
        ))
