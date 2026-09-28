from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
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

