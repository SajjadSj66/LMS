from django.db import models
from users.models import *
from library.models import *

class BorrowingTransaction(models.Model):
    borrower = models.ForeignKey(Borrower, on_delete=models.CASCADE, related_name='borrowing_history')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrowed_by')
    borrowed_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    returned_date = models.DateField(null=True, blank=True)

    def is_overdue(self):
        return self.returned_date is None and date.today() > self.due_date

    def __str__(self):
        return f"{self.borrower.user.username} borrowed {self.book.title}"


class Reservation(models.Model):
    borrower = models.ForeignKey(Borrower, related_name='reservation', on_delete=models.CASCADE)
    book = models.ForeignKey(Book, related_name='reservations', on_delete=models.CASCADE)
    reservation_date = models.DateField(auto_now_add=True)
    notified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.borrower.user.username} reserved {self.book.title}"