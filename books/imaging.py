"""Rasmlarni optimallashtirish yordamchilari.

Yuklangan rasmlar ko'pincha telefon kamerasidan (4000x3000+, bir necha MB)
keladi. Brauzer ularni to'liq o'lchamda xotiraga ochadi
(kenglik x balandlik x 4 bayt), bu esa juda ko'p RAM sarflaydi.
Bu yerda rasm yuklangach uni kichraytirib, qayta siqamiz.
"""
import os

from PIL import Image, ImageOps

# Qayta siqishni qaytadan ishga tushirmaslik uchun fayl hajmi chegarasi
_HEAVY_BYTES = 300 * 1024  # 300 KB


def optimize_image_field(image_field, max_w, max_h, quality=82):
    """Saqlangan rasmni joyida kichraytirib qayta siqadi (lokal storage).

    Idempotent: rasm allaqachon chegara ichida bo'lsa va yengil bo'lsa,
    hech narsa qilmaydi — shu sababli har bir save'da xavfsiz chaqirsa bo'ladi.
    """
    if not image_field:
        return
    try:
        path = image_field.path
    except (ValueError, NotImplementedError):
        # Lokal bo'lmagan storage (masalan S3) — path yo'q, o'tkazib yuboramiz
        return
    try:
        img = Image.open(path)
    except (FileNotFoundError, OSError):
        return

    fmt = (img.format or 'JPEG').upper()
    img = ImageOps.exif_transpose(img)  # kamera orientatsiyasini hisobga olamiz

    too_big = img.width > max_w or img.height > max_h
    try:
        heavy = os.path.getsize(path) > _HEAVY_BYTES
    except OSError:
        heavy = False
    if not too_big and not heavy:
        return  # allaqachon optimal — qayta yozmaymiz

    if fmt == 'PNG' and img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGBA')
        save_fmt, save_kwargs = 'PNG', {'optimize': True}
    elif fmt == 'WEBP':
        img = img.convert('RGB')
        save_fmt, save_kwargs = 'WEBP', {'quality': quality, 'method': 6}
    else:
        img = img.convert('RGB')
        save_fmt = 'JPEG'
        save_kwargs = {'quality': quality, 'optimize': True, 'progressive': True}

    if too_big:
        img.thumbnail((max_w, max_h), Image.LANCZOS)

    img.save(path, save_fmt, **save_kwargs)
