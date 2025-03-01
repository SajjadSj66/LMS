from django.test import TestCase
from library.models import *
from datetime import date, timedelta
from users.models import *
from transactions.models import BorrowingTransaction


class BorrowingTransactionViewSetTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser3", password="password")
        self.borrower = Borrower.objects.create(user=self.user)
        self.author = Author.objects.create(name="Test Author 3")
        self.book = Book.objects.create(
            title="Test Book 3",
            author=self.author,
            isbn="1928374650123",
            publication_date=date.today(),
            is_available=True
        )
        self.transaction = BorrowingTransaction.objects.create(
            borrower=self.borrower,
            book=self.book,
            due_date=date.today() + timedelta(days=14)
        )

    def test_borrow_book(self):
        self.assertEqual(self.transaction.book, self.book)
        self.assertEqual(self.transaction.borrower, self.borrower)
        self.assertEqual(self.transaction.due_date, date.today() + timedelta(days=14))

    def test_return_book(self):
        self.transaction.returned_date = date.today()
        self.transaction.book.is_available = True
        self.transaction.save()
        self.assertTrue(self.transaction.returned_date)
        self.assertTrue(self.transaction.book.is_available)
