from django.db import models
from django.contrib.auth.models import User

from books.imaging import optimize_image_field
# Create your models here.

class Profil(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(max_length=300, blank=True)
    telegram = models.CharField(max_length=50,blank=True)
    telefon = models.CharField(max_length=15,blank=True)
    instagram = models.CharField(max_length=50,blank=True)

    def __str__(self):
        return f"{self.user.username} profili"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Avatar kichik ko'rsatiladi — 400px yetarli
        optimize_image_field(self.avatar, max_w=400, max_h=400)

    @property
    def bosh_harf(self):
        """Avatar bo'lmaganda ko'rsatish uchun foydalanuvchi nomining bosh harfi."""
        return self.user.username[:1].upper() if self.user.username else "?"


class Bildirishnoma(models.Model):
    TURI_TANLOV = [
        ('info', 'Info'),
        ('success', 'Muvaffaqiyat'),
        ('warning', 'Ogohlantirish'),
    ]
    foydalanuvchi = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bildirishnomalar')
    matn = models.CharField(max_length=255)
    havola = models.CharField(max_length=200, blank=True)
    turi = models.CharField(max_length=20, choices=TURI_TANLOV, default='info')
    oqilgan = models.BooleanField(default=False)
    yaratildi = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-yaratildi']

    def __str__(self):
        return f"{self.foydalanuvchi.username}: {self.matn[:30]}"
    
class TasdiqlashKodi(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    kod = models.CharField(max_length=6)
    yaratildi = models.DateTimeField(auto_now_add=True)
    tasdiqlangan = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.user_permissions} - {self.kod}"