from unittest.mock import patch
from datetime import timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase
from rest_framework import status

from accounts.models import TasdiqlashKodi
from accounts.services import royxatdan_otish_service, tasdiqlash_kodi_tekshirish_service

User = get_user_model()


class AccountsServiceTestCase(TestCase):

    def test_registration_smtp_failure_rolls_back_user(self):
        """SMTP xatosi yuz berganda DB da user qolib ketmasligi (Rollback) kerak."""
        with patch('accounts.services.send_mail', side_effect=Exception('SMTP server unreachable')):
            with self.assertRaises(ValidationError):
                royxatdan_otish_service('testuser', 'test@gmail.com', 'Pass12345')

        # DB da 'testuser' yaratilmagan (roll back bo'lgan) bo'lishi kerak
        self.assertFalse(User.objects.filter(username='testuser').exists())

    def test_otp_5_attempts_limit(self):
        """5 marta noto'g'ri kod kiritilgach bloklanishi kerak."""
        user, tasdiqlash = royxatdan_otish_service('testuser2', 'test2@gmail.com', 'Pass12345')
        
        # 4 marta noto'g'ri kiritamiz
        for _ in range(4):
            with self.assertRaises(ValidationError):
                tasdiqlash_kodi_tekshirish_service(user.id, '000000')

        # 5-marta urinish xato bergach limit oshadi
        with self.assertRaises(ValidationError):
            tasdiqlash_kodi_tekshirish_service(user.id, '000000')

        # 6-urinishda limitdan oshdi degan xato beradi
        with self.assertRaises(ValidationError) as cm:
            tasdiqlash_kodi_tekshirish_service(user.id, '000000')
        self.assertIn('cheklovdan oshdi', str(cm.exception))

    def test_otp_replay_attack_prevented(self):
        """Kod bir marta ishlatilgach, uni qayta ishlatish (Replay attack) taqiqlanadi."""
        user, tasdiqlash = royxatdan_otish_service('testuser3', 'test3@gmail.com', 'Pass12345')
        to_gri_kod = tasdiqlash.kod

        # Birinchi marta to'g'ri kod kiritamiz -> muvaffaqiyatli
        active_user, t_obj = tasdiqlash_kodi_tekshirish_service(user.id, to_gri_kod)
        self.assertTrue(active_user.is_active)
        self.assertTrue(t_obj.tasdiqlangan)

        # Xuddi shu kodni takroran yuborish (Replay) taqiqlanadi
        with self.assertRaises(ValidationError) as cm:
            tasdiqlash_kodi_tekshirish_service(user.id, to_gri_kod)
        self.assertIn('topilmadi', str(cm.exception))

    def test_otp_expired_after_10_minutes(self):
        """10 daqiqadan keyin OTP kod eskirishi kerak."""
        user, tasdiqlash = royxatdan_otish_service('testuser4', 'test4@gmail.com', 'Pass12345')
        to_gri_kod = tasdiqlash.kod

        # 11 daqiqa kelajakka suramiz
        future_time = timezone.now() + timedelta(minutes=11)
        with patch('django.utils.timezone.now', return_value=future_time):
            with self.assertRaises(ValidationError) as cm:
                tasdiqlash_kodi_tekshirish_service(user.id, to_gri_kod)
            self.assertIn('tugagan', str(cm.exception))


class AccountsWebViewsTestCase(TestCase):

    def setUp(self):
        self.client = Client()

    @patch('accounts.services.send_mail')
    def test_web_registration_and_activation_flow(self, mock_send_mail):
        """Web sahifa orqali ro'yxatdan o'tish va tasdiqlash oqimi."""
        # 1. Ro'yxatdan o'tish
        url_reg = reverse('royxatdan-otish')
        res_reg = self.client.post(url_reg, {
            'username': 'webuser',
            'email': 'webuser@gmail.com',
            'password1': 'Pass12345!',
            'password2': 'Pass12345!'
        })
        self.assertEqual(res_reg.status_code, 302)  # Redirect to tasdiqlash
        user = User.objects.get(username='webuser')
        self.assertFalse(user.is_active)

        # Session da tasdiqlash_user_id bo'lishi kerak
        tasdiqlash_kodi = TasdiqlashKodi.objects.get(user=user)

        # 2. Tasdiqlash sahifasiga POST yuborish
        url_tas = reverse('tasdiqlash')
        res_tas = self.client.post(url_tas, {'kod': tasdiqlash_kodi.kod})
        self.assertEqual(res_tas.status_code, 302)  # Redirect to kitoblar-royhati

        user.refresh_from_db()
        self.assertTrue(user.is_active)


class AccountsAPITestCase(APITestCase):

    @patch('accounts.services.send_mail')
    def test_api_register_and_tasdiqlash_flow(self, mock_send_mail):
        """REST API orqali ro'yxatdan o'tish va tasdiqlash."""
        # 1. API Register
        reg_url = reverse('api-register')
        reg_data = {
            'username': 'apiuser',
            'email': 'apiuser@gmail.com',
            'password': 'Password123!'
        }
        res_reg = self.client.post(reg_url, reg_data, format='json')
        self.assertEqual(res_reg.status_code, status.HTTP_201_CREATED)
        user_id = res_reg.data['user_id']

        user = User.objects.get(id=user_id)
        tasdiqlash = TasdiqlashKodi.objects.get(user=user)

        # 2. API Tasdiqlash
        tas_url = reverse('api-tasdiqlash')
        tas_data = {
            'user_id': user_id,
            'kod': tasdiqlash.kod
        }
        res_tas = self.client.post(tas_url, tas_data, format='json')
        self.assertEqual(res_tas.status_code, status.HTTP_200_OK)
        self.assertIn('token', res_tas.data)

        user.refresh_from_db()
        self.assertTrue(user.is_active)
