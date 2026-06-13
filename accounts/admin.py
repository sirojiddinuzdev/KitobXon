from django.contrib import admin
from .models import Profil, Bildirishnoma


@admin.register(Profil)
class ProfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'telegram', 'telefon')
    search_fields = ('user__username',)


@admin.register(Bildirishnoma)
class BildirishnomaAdmin(admin.ModelAdmin):
    list_display = ('foydalanuvchi', 'matn', 'turi', 'oqilgan', 'yaratildi')
    list_filter = ('turi', 'oqilgan')
    search_fields = ('foydalanuvchi__username', 'matn')
