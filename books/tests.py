from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from books.models import Kitob, Sharh
from django.contrib.auth import get_user_model

User = get_user_model()


class KitobViewSetTestCase(APITestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='testpass1')
        self.user2 = User.objects.create_user(username='user2', password='testpass2')

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
        # Agar pagination bo'lsa 'results' ichida qaytadi
        data = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(data), 2)

    def test_kitob_filter_by_janr(self):
        url = reverse('api-kitob-list') + '?janr=it'
        self.client.force_authenticate(self.user1)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(data), 1)  # Faqat 1 ta kitob 'it' janrida
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
        self.assertEqual(response.data['ortacha_baho'], 4.5)  # (5+4) / 2

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
        # user1 boshqaning kitobiga (kitob2) sharh qoldiradi
        url = reverse('api-kitob-sharh', args=[self.kitob2.id])
        self.client.force_authenticate(self.user1)
        data = {'baho': 5, 'matn': 'Ajoyib asar!'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['baho'], 5)

    def test_kitob_sharh_cannot_review_own_book(self):
        # user1 o'zining kitobiga (kitob1) sharh qoldirolmasligi kerak
        url = reverse('api-kitob-sharh', args=[self.kitob1.id])
        self.client.force_authenticate(self.user1)
        data = {'baho': 5, 'matn': 'Zor!'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
