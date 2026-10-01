import unittest
import unittest.mock
from django.urls import reverse
from django.test import TestCase, TransactionTestCase, Client
from django.conf import settings
from rest_framework import status
from rest_framework.test import APITestCase
from books.models import Kitob, Sharh, Almashitirish, Sevimli
from django.contrib.auth import get_user_model


User = get_user_model()

# PostgreSQL mavjudligini tekshiramiz
def _is_postgres():
    db = settings.DATABASES.get('default', {})
    return 'postgresql' in db.get('ENGINE', '') or 'postgis' in db.get('ENGINE', '')


class KitobViewSetTestCase(APITestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='testpass1')
        self.user2 = User.objects.create_user(username='user2', password='testpass2')
        self.user3 = User.objects.create_user(username='user3', password='testpass3')

        self.kitob1 = Kitob.objects.create(
            nomi='Python Asoslari', 
            muallif='Ali Valiyev', 
            janr='it',
            hudud='toshkent',
            ega=self.user1
        )
        self.kitob2 = Kitob.objects.create(
            nomi='Sariq devni minib', 
            muallif='Xudoyberdi To\'xtaboyev', 
            janr='badiiy',
            hudud='samarkand',
            ega=self.user2
        )

        Sharh.objects.create(kitob=self.kitob1, muallif=self.user2, baho=5, matn="Zo'r kitob")
        Sharh.objects.create(kitob=self.kitob1, muallif=self.user1, baho=4, matn="Yaxshi")

    def test_kitob_list(self):
        url = reverse('api-kitob-list')
        self.client.force_authenticate(self.user1)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(data), 2)

    def test_kitob_filter_by_janr(self):
        url = reverse('api-kitob-list') + '?janr=it'
        self.client.force_authenticate(self.user1)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['nomi'], 'Python Asoslari')

    def test_kitob_detail(self):
        url = reverse('api-kitob-detail', args=[self.kitob1.id])
        self.client.force_authenticate(self.user1)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nomi'], 'Python Asoslari')

    def test_average_rating(self):
        url = reverse('api-kitob-detail', args=[self.kitob1.id])
        self.client.force_authenticate(self.user1)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['ortacha_baho'], 4.5)

    def test_permission_denied_for_anonymous_create(self):
        self.client.force_authenticate(user=None)
        url = reverse('api-kitob-list')
        data = {'nomi': 'Test Kitob', 'muallif': 'Test Muallif', 'janr': 'it'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_permission_granted_for_authenticated_create(self):
        url = reverse('api-kitob-list')
        self.client.force_authenticate(self.user1)
        data = {'nomi': 'Test Kitob', 'muallif': 'Test Muallif', 'janr': 'it'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['nomi'], 'Test Kitob')

    def test_kitob_sharh_leave_review(self):
        url = reverse('api-kitob-sharh', args=[self.kitob2.id])
        self.client.force_authenticate(self.user1)
        data = {'baho': 5, 'matn': 'Ajoyib asar!'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['baho'], 5)

    def test_kitob_sharh_cannot_review_own_book(self):
        url = reverse('api-kitob-sharh', args=[self.kitob1.id])
        self.client.force_authenticate(self.user1)
        data = {'baho': 5, 'matn': 'Zor!'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_almashitirish_state_machine_prevents_re_transition(self):
        sorov = Almashitirish.objects.create(kitob=self.kitob1, yuboruvchi=self.user2)
        
        self.client.force_authenticate(self.user1)
        qabul_url = reverse('api-sorov-qabul', args=[sorov.id])
        res1 = self.client.post(qabul_url)
        self.assertEqual(res1.status_code, status.HTTP_200_OK)
        
        self.kitob1.refresh_from_db()
        self.assertFalse(self.kitob1.mavjud)

        # Allaqachon qabul qilingan so'rovni qayta rad etish taqiqlanadi
        rad_url = reverse('api-sorov-rad', args=[sorov.id])
        res2 = self.client.post(rad_url)
        self.assertEqual(res2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_almashitirish_accept_rejects_other_pending_requests(self):
        # user2 va user3 bir vaqtda kitob1 uchun so'rov yuboradi
        sorov2 = Almashitirish.objects.create(kitob=self.kitob1, yuboruvchi=self.user2)
        sorov3 = Almashitirish.objects.create(kitob=self.kitob1, yuboruvchi=self.user3)

        self.client.force_authenticate(self.user1)
        qabul_url = reverse('api-sorov-qabul', args=[sorov2.id])
        res = self.client.post(qabul_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        sorov2.refresh_from_db()
        sorov3.refresh_from_db()
        self.assertEqual(sorov2.holat, 'qabul')
        self.assertEqual(sorov3.holat, 'rad')  # Boshqa kutilayotgan so'rov avtomatik rad bo'lishi kerak


class BooksWebViewsTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='webuser1', password='pass1')
        self.user2 = User.objects.create_user(username='webuser2', password='pass2')
        self.kitob = Kitob.objects.create(nomi='Test Book', muallif='Author', janr='it', ega=self.user1)

    def test_sorov_yuborish_get_disallowed(self):
        """GET orqali so'rov yuborish taqiqlangan bo'lishi (405 Method Not Allowed) kerak."""
        self.client.force_login(self.user2)
        url = reverse('sorov-yuborish', args=[self.kitob.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

    def test_sorov_yuborish_post_success(self):
        """POST orqali so'rov muvaffaqiyatli yuborilishi kerak."""
        self.client.force_login(self.user2)
        url = reverse('sorov-yuborish', args=[self.kitob.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Almashitirish.objects.filter(kitob=self.kitob, yuboruvchi=self.user2).exists())

    def test_sorov_qabul_get_disallowed(self):
        """GET orqali so'rovni qabul qilish taqiqlangan bo'lishi (405 Method Not Allowed) kerak."""
        sorov = Almashitirish.objects.create(kitob=self.kitob, yuboruvchi=self.user2)
        self.client.force_login(self.user1)
        url = reverse('sorov-qabul', args=[sorov.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

    def test_sorov_rad_get_disallowed(self):
        """GET orqali so'rovni rad etish taqiqlangan bo'lishi (405 Method Not Allowed) kerak."""
        sorov = Almashitirish.objects.create(kitob=self.kitob, yuboruvchi=self.user2)
        self.client.force_login(self.user1)
        url = reverse('sorov-rad', args=[sorov.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

    def test_open_redirect_prevented_in_sorov_yuborish(self):
        """?next= orqali tashqi saytga open redirect taqiqlanishi kerak (xavfsizlik)."""
        self.client.force_login(self.user2)
        url = reverse('sorov-yuborish', args=[self.kitob.id])
        # Tashqi URL ga yo'naltirishga urinish
        response = self.client.post(url, data={'next': 'https://zararli.com'})
        # 302 bo'lishi kerak, lekin tashqi URL ga EMAS
        self.assertEqual(response.status_code, 302)
        redirect_url = response['Location']
        self.assertFalse(
            redirect_url.startswith('https://zararli.com'),
            f"Open redirect aniqlandi: {redirect_url}"
        )

    def test_open_redirect_prevented_in_sevimli(self):
        """sevimli_toggle da ?next= orqali tashqi saytga open redirect taqiqlanishi kerak."""
        self.client.force_login(self.user2)
        url = reverse('sevimli-toggle', args=[self.kitob.id])
        response = self.client.post(url, data={'next': 'https://phishing.com'})
        self.assertEqual(response.status_code, 302)
        redirect_url = response['Location']
        self.assertFalse(
            redirect_url.startswith('https://phishing.com'),
            f"Open redirect aniqlandi: {redirect_url}"
        )


@unittest.skipUnless(_is_postgres(), "Bu test faqat PostgreSQL bilan ishlaydigan muhitda o'tkaziladi (SQLite row locking'ni qo'llab-quvvatlamaydi)")
class PostgreSQLConcurrencyTestCase(TransactionTestCase):
    """
    PostgreSQL select_for_update (Row Locking) ni isbotlovchi test.

    TransactionTestCase ishlatiladi — oddiy TestCase barcha testlarni bitta
    tranzaksiya ichida o'raydi, shuning uchun parallel threadlar yangi
    ma'lumotlarni ko'ra olmaydi. TransactionTestCase har test uchun haqiqiy
    COMMIT qiladi, bu esa real concurrency sinoviga imkon beradi.
    """

    def setUp(self):
        self.user1 = User.objects.create_user(username='lock_user1', password='pass')
        self.user2 = User.objects.create_user(username='lock_user2', password='pass')
        self.user3 = User.objects.create_user(username='lock_user3', password='pass')
        self.kitob = Kitob.objects.create(
            nomi='Locking Testi', muallif='Test', janr='it', ega=self.user1
        )

    @unittest.mock.patch('books.services.sorov_qabul_email')
    def test_double_accept_only_one_succeeds(self, mock_email):
        """
        Bitta kitobga ikki so'rov bor. Ikkalasi bir vaqtda qabul qilinmoqchi bo'lsa,
        faqat bittasi o'tishi va kitob holati izchil bo'lishi kerak.
        """
        from threading import Thread, Barrier
        from django.db import close_old_connections
        from books.services import qabul_qilish_service

        sorov2 = Almashitirish.objects.create(kitob=self.kitob, yuboruvchi=self.user2)
        sorov3 = Almashitirish.objects.create(kitob=self.kitob, yuboruvchi=self.user3)

        results = []
        # Barrier: ikkala thread ham bir vaqtda boshlansin
        barrier = Barrier(2)

        def try_accept(sorov_id):
            # Thread-ga yangi DB connection berish
            close_old_connections()
            try:
                barrier.wait()  # Ikkalasi tayyor bo'lgunicha kutish
                qabul_qilish_service(sorov_id, self.user1)
                results.append('success')
            except Exception:
                results.append('failed')
            finally:
                close_old_connections()

        t1 = Thread(target=try_accept, args=[sorov2.id])
        t2 = Thread(target=try_accept, args=[sorov3.id])
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        # Faqat bittasi muvaffaqiyatli bo'lishi kerak
        self.assertEqual(results.count('success'), 1, f"Natijalar: {results}")
        self.assertEqual(results.count('failed'), 1, f"Natijalar: {results}")

        # Kitob bazada band holida bo'lishi kerak
        self.kitob.refresh_from_db()
        self.assertFalse(self.kitob.mavjud)
