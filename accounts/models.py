from django.db import models
from django.contrib.auth.models import User
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

    @property
    def bosh_harf(self):
        """Avatar bo'lmaganda ko'rsatish uchun foydalanuvchi nomining bosh harfi."""
        return self.user.username[:1].upper() if self.user.username else "?"