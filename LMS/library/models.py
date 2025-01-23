from datetime import date

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Avg
from rest_framework import permissions


# Create your models here.
# User Model
class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('borrower', 'Borrower'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='borrower')


# Permission
class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsBorrowerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role == 'borrower'


class Author(models.Model):
    name = models.CharField(max_length=100)
    biography = models.TextField(default='')
    nationality = models.CharField(max_length=100, default='unknown')
    date_of_birth = models.DateField(default=date.today)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(default='')
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    isbn = models.CharField(max_length=13, unique=True)
    category = models.CharField(max_length=255, default='')
    publication_date = models.DateField()
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def average_rating(self):
        return self.reviews.aggregate(average=Avg('rating'))['average'] or 0


class Borrower(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='borrower_profile', blank=True, null=True)
    registration_date = models.DateField(auto_now_add=True, null=True)

    def __str__(self):
        return self.user.username


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


class Review(models.Model):
    borrower = models.ForeignKey(Borrower, related_name='reviews', on_delete=models.CASCADE)
    book = models.ForeignKey(Book, related_name='reviews', on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField()
    review_date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('borrower', 'book')

    def __str__(self):
        return f"Review by {self.borrower.user.username} for {self.book.title}"
