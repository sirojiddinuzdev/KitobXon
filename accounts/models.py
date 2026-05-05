from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Profil(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    telegram = models.CharField(max_length=50,blank=True)
    telefon = models.CharField(max_length=15,blank=True)
    instagram = models.CharField(max_length=50,blank=True)

    def __str__(self):
        return f"{self.user.username} profili"