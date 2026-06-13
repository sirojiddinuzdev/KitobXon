from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.royhatdan_otish, name='royxatdan-otish'),
    path('login/', views.kirish, name='kirish'),
    path('logout/', views.chiqish, name='chiqish'),
    path('profil/', views.profil, name='profil'),
    path('bildirishnomalar/', views.bildirishnomalar, name='bildirishnomalar'),

    # Parolni tiklash (Django built-in)
    path('parol/tiklash/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset.html',
        email_template_name='accounts/password_reset_email.html',
        subject_template_name='accounts/password_reset_subject.txt',
        success_url='/accounts/parol/tiklash/yuborildi/',
    ), name='parol-tiklash'),
    path('parol/tiklash/yuborildi/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html',
    ), name='password_reset_done'),
    path('parol/tasdiqlash/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html',
        success_url='/accounts/parol/bajarildi/',
    ), name='password_reset_confirm'),
    path('parol/bajarildi/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html',
    ), name='password_reset_complete'),
]
