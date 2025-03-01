from rest_framework.test import APITestCase
from rest_framework import status
from library.models import *
from django.urls import reverse


class BookViewSetTest(APITestCase):
    def setUp(self):
        self.author = Author.objects.create(name="Test Author")
        self.book = Book.objects.create(
            title="Test Book",
            author=self.author,
            isbn="1234567890123",
            publication_date="2023-01-01"
        )
        self.book_url = reverse('book-list')

    def test_get_books(self):
        response = self.client.get(self.book_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
