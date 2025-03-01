from django.test import TestCase
from library.tasks import *


class CeleryTaskTest(TestCase):
    def test_generate_most_borrowed_books_report(self):
        result = generate_most_borrowed_books_report.delay()
        self.assertIsNotNone(result.id)

    def test_generate_overdue_borrowers_report(self):
        result = generate_overdue_borrowers_report.delay()
        self.assertIsNotNone(result.id)

    def test_generate_checked_out_books_report(self):
        result = generate_checked_out_books_report.delay()
        self.assertIsNotNone(result.id)
