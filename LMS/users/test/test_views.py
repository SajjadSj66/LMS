from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from users.models import *


class UserViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass', role='admin')
        self.client.login(username='testuser', password='testpass')
        self.user_url = reverse('user-list')

    def test_get_users(self):
        response = self.client.get(self.user_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class BorrowerViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='borroweruser', password='testpass', role='borrower')
        self.borrower = Borrower.objects.create(user=self.user)
        self.client.login(username='borroweruser', password='testpass')
        self.borrower_url = reverse('borrower-list')

    def test_get_borrowers(self):
        response = self.client.get(self.borrower_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
