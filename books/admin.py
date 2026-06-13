from django.contrib import admin
from .models import Kitob, Almashitirish, Sevimli, Sharh, Istak


@admin.register(Kitob)
class KitobAdmin(admin.ModelAdmin):
    list_display = ('nomi', 'muallif', 'janr', 'hudud', 'ega', 'mavjud', 'yaratildi')
    list_filter = ('janr', 'hudud', 'mavjud')
    search_fields = ('nomi', 'muallif')
    list_editable = ('mavjud',)
    date_hierarchy = 'yaratildi'


@admin.register(Almashitirish)
class AlmashitirishAdmin(admin.ModelAdmin):
    list_display = ('kitob', 'yuboruvchi', 'holat', 'yaratildi')
    list_filter = ('holat',)
    search_fields = ('kitob__nomi', 'yuboruvchi__username')


@admin.register(Sevimli)
class SevimliAdmin(admin.ModelAdmin):
    list_display = ('foydalanuvchi', 'kitob', 'yaratildi')
    search_fields = ('foydalanuvchi__username', 'kitob__nomi')


@admin.register(Sharh)
class SharhAdmin(admin.ModelAdmin):
    list_display = ('kitob', 'muallif', 'baho', 'yaratildi')
    list_filter = ('baho',)
    search_fields = ('kitob__nomi', 'muallif__username')


@admin.register(Istak)
class IstakAdmin(admin.ModelAdmin):
    list_display = ('nomi', 'muallif', 'foydalanuvchi', 'topildi', 'yaratildi')
    list_filter = ('topildi',)
    search_fields = ('nomi', 'foydalanuvchi__username')
