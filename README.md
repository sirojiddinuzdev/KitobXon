# KitobXon

Kitob almashtirish uchun platforma. Foydalanuvchilar o'qib bo'lgan kitoblarini boshqalar bilan almashishi mumkin.

## Ishlatilgan texnologiyalar

- Django
- PostgreSQL
- Redis
- Celery
- Docker
- Nginx
- AWS EC2

## Funksiyalar

- Kitob qo'shish, tahrirlash va o'chirish
- Kitob detali sahifasi va o'xshash kitoblar tavsiyasi
- Kitob qidirish (nom/muallif)
- Janr va hudud bo'yicha filter
- Sahifalash (pagination)
- Sevimli kitoblar (favorites)
- Kitob so'rovi yuborish, qabul yoki rad qilish
- Kelgan so'rovlar uchun navbar bildirishnoma belgisi
- Foydalanuvchi profili: avatar, bio va statistika paneli
- Email xabarnoma (Celery)
- REST API va Swagger
- Zamonaviy, mobilga moslashgan dizayn

## REST API

Token autentifikatsiya (DRF). Swagger: `/api/swagger/`, schema: `/api/schema/`.

Autentifikatsiya — `Authorization: Token <token>` sarlavhasi.

| Metod | Endpoint | Tavsif |
|-------|----------|--------|
| POST | `/api/auth/register/` | Ro'yxatdan o'tish → token |
| POST | `/api/auth/login/` | Kirish → token |
| GET | `/api/auth/me/` | Joriy foydalanuvchi |
| GET/PUT/PATCH | `/api/profil/` | O'z profili |
| GET | `/api/kitoblar/` | Ro'yxat (`?q=&janr=&hudud=&mavjud=&mine=`) |
| POST | `/api/kitoblar/` | Kitob qo'shish (auth) |
| GET/PUT/PATCH/DELETE | `/api/kitoblar/{id}/` | Batafsil / tahrir / o'chirish (egasi) |
| GET | `/api/kitoblar/{id}/sharhlar/` | Kitob sharhlari |
| POST | `/api/kitoblar/{id}/sharh/` | Sharh + baho (1–5) qoldirish |
| POST | `/api/kitoblar/{id}/sevimli/` | Sevimliga qo'shish/olib tashlash |
| POST | `/api/kitoblar/{id}/sorov/` | Almashtirish so'rovi yuborish |
| GET | `/api/sevimlilar/` | Sevimli kitoblar |
| GET | `/api/sorovlar/` | So'rovlar (`?turi=kelgan` yoki `yuborilgan`) |
| POST | `/api/sorovlar/{id}/qabul/` | So'rovni qabul qilish (egasi) |
| POST | `/api/sorovlar/{id}/rad/` | So'rovni rad etish (egasi) |
| GET | `/api/bildirishnomalar/` | Bildirishnomalar |
| POST | `/api/bildirishnomalar/oqildi/` | Hammasini o'qilgan deb belgilash |

## Demo

[https://www.kitobhon.uz](https://www.kitobhon.uz)
