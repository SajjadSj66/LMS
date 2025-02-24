from drf_spectacular.utils import extend_schema
from django.core.mail import send_mail
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from celery import shared_task
from transactions.models import BorrowingTransaction, Reservation
from users.permission import IsBorrowerOrReadOnly
from .models import *
from .serializers import *
from .pagination import *
from .tasks import *


# Create your views here.
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return []
        return [IsAuthenticated()]

    @extend_schema(
        summary="Retrieve all books",
        description="Returns a list of all books with pagination support.",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve a specific book",
        description="Returns detailed information about a single book by its ID.",
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return []
        return [IsAuthenticated()]


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsBorrowerOrReadOnly]


# Celery Task
@shared_task
def send_due_date_reminders():
    transactions = BorrowingTransaction.objects.filter(returned_date__isnull=True)
    today = date.today()
    for transaction in transactions:
        days_left = (transaction.due_date - today).days
        if days_left == 1:
            send_mail(
                subject='Book Due Date Reminder',
                message=f"Dear {transaction.borrower.user.username}, your book '{transaction.book.title}' is due tomorrow.",
                from_email='<EMAIL>',
                recipient_list=[transaction.borrower.user.email],
            )
        elif transaction.is_overdue():
            send_mail(
                subject='Overdue Book Reminder',
                message=f"Dear {transaction.borrower.user.username}, your book '{transaction.book.title}' is overdue. Please return it as soon as possible.",
                from_email='<EMAIL>',
                recipient_list=[transaction.borrower.user.email],
            )


@shared_task
def process_reservation():
    reservations = Reservation.objects.filter(notified=False, book__is_available=True)
    for reservation in reservations:
        send_mail(
            subject="Book Now Available",
            message=f"Dear {reservation.borrower.user.username}, the book '{reservation.book.title}' you reserved is now available.",
            from_email='<EMAIL>',
            recipient_list=[reservation.borrower.user.email],
        )
        reservation.notified = True
        reservation.save()


class ReportViewSet(viewsets.ModelViewSet):
    @action(detail=False, methods=['post'], url_path='most-borrowed')
    def most_borrowed(self, request):
        task = generate_most_borrowed_books_report.delay()
        return Response({"task_id": task.id, "status": "Processing"})

    @action(detail=False, methods=['post'], url_path='overdue-borrowers')
    def overdue_borrowers(self, request):
        task = generate_overdue_borrowers_report.delay()
        return Response({"task_id": task.id, "status": "Processing"})

    @action(detail=False, methods=['post'], url_path='checked-out')
    def checked_out(self, request):
        task = generate_checked_out_books_report.delay()
        return Response({"task_id": task.id, "status": "Processing"})