from django.test import TestCase
from library.models import *


class AuthorModelTest(TestCase):
    def setUp(self):
        self.author = Author.objects.create(name="Test Author", nationality="Test Nationality")

    def test_author_creation(self):
        self.assertEqual(self.author.name, "Test Author")
        self.assertEqual(self.author.nationality, "Test Nationality")

    def test_author_str(self):
        self.assertEqual(str(self.author), "Test Author")


class BookModelTest(TestCase):
    def setUp(self):
        self.author = Author.objects.create(name="Test Author")
        self.book = Book.objects.create(
            title="Test Book",
            author=self.author,
            isbn="1234567890123",
            publication_date="2023-01-01"
        )

    def test_book_creation(self):
        self.assertEqual(self.book.title, "Test Book")

    def test_book_str(self):
        self.assertEqual(str(self.book), "Test Book")


class ReviewModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.borrower = Borrower.objects.create(user=self.user)
        self.author = Author.objects.create(name="Test Author")
        self.book = Book.objects.create(
            title="Test Book",
            author=self.author,
            isbn="1234567890123",
            publication_date="2023-01-01"
        )
        self.review = Review.objects.create(
            borrower=self.borrower,
            book=self.book,
            rating=5,
            comment="Great book!"
        )

    def test_review_creation(self):
        self.assertEqual(self.review.rating, 5)
        self.assertEqual(self.review.comment, "Great book!")

    def test_review_str(self):
        self.assertEqual(str(self.review),
                         f"Review by {self.review.borrower.user.username} for {self.review.book.title}")
