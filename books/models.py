from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Kitob(models.Model):
    Janr_Tanlov = [     
        ('badiiy','Badiiy'),
        ('Selfhelp','Self Help')
    ]
    nomi = models.CharField(max_length=200)
    muallif = models.CharField(max_length=100)
    tavsif = models.TextField(blank=True,null=True)
    janr = models.CharField(max_length=20,choices=Janr_Tanlov,default='boshqa')
    rasm = models.ImageField(upload_to='books/',blank=True,null=True)
    ega = models.ForeignKey(User,on_delete=models.CASCADE,related_name='books')
    mavjud = models.BooleanField(default=True)
    yaratildi = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nomi} - {self.muallif}"
