from django.test import TestCase
from transactions.models import *
from library.models import *
from users.models import *
from datetime import date, timedelta



class BorrowingTransactionTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.borrower = Borrower.objects.create(user=self.user)
        self.author = Author.objects.create(name="Test Author")
        self.book = Book.objects.create(
            title="Test Book",
            author=self.author,
            isbn="1234567890123",
            publication_date=date.today(),
            is_available=True
        )
        self.transaction = BorrowingTransaction.objects.create(
            borrower=self.borrower,
            book=self.book,
            due_date=date.today() + timedelta(days=14)
        )

    def test_borrowing_transaction_creation(self):
        self.assertEqual(self.transaction.borrower, self.borrower)
        self.assertEqual(self.transaction.book, self.book)
        self.assertFalse(self.transaction.is_overdue())

    def test_overdue_status(self):
        self.transaction.due_date = date.today() - timedelta(days=1)
        self.transaction.save()
        self.assertTrue(self.transaction.is_overdue())


class ReservationTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser2", password="password")
        self.borrower = Borrower.objects.create(user=self.user)
        self.author = Author.objects.create(name="Test Author 2")
        self.book = Book.objects.create(
            title="Test Book 2",
            author=self.author,
            isbn="9876543210123",
            publication_date=date.today(),
            is_available=True
        )
        self.reservation = Reservation.objects.create(
            borrower=self.borrower,
            book=self.book
        )

    def test_reservation_creation(self):
        self.assertEqual(self.reservation.borrower, self.borrower)
        self.assertEqual(self.reservation.book, self.book)
        self.assertFalse(self.reservation.notified)
