from django.test import TestCase
from users.models import *


class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass', role='borrower')

    def test_user_creation(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.role, 'borrower')

    def test_user_str(self):
        self.assertEqual(str(self.user), 'testuser')


class BorrowerModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='borroweruser', password='testpass', role='borrower')
        self.borrower = Borrower.objects.create(user=self.user)

    def test_borrower_creation(self):
        self.assertEqual(self.borrower.user.username, 'borroweruser')

    def test_borrower_str(self):
        self.assertEqual(str(self.borrower), 'borroweruser')