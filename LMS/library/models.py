from datetime import date
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Avg
from users.models import *

# Create your models here.
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
