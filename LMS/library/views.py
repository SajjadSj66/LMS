from datetime import timedelta

from django.conf import settings
from drf_spectacular.utils import extend_schema
from django.core.mail import send_mail
from django.shortcuts import render
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from celery import shared_task
from .models import *
from .serializers import *
from .pagination import *
from .tasks import *


# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    pagination_class = CustomPagination
    authentication_classes = [JWTAuthentication]

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
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return []
        return [IsAuthenticated()]


class BorrowerViewSet(viewsets.ModelViewSet):
    queryset = Borrower.objects.all()
    serializer_class = BorrowerSerializer
    pagination_class = CustomPagination
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


class BorrowingTransactionViewSet(viewsets.ModelViewSet):
    queryset = BorrowingTransaction.objects.all()
    serializer_class = BorrowingTransactionSerializer
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated()]
        return [IsAdminUser()]

    @action(detail=False, methods=['post'], url_path='borrow')
    def borrow_book(self, request):
        borrower_id = request.data.get('borrower_profile')
        book_id = request.data.get('book')

        try:
            borrower = Borrower.objects.get(id=borrower_id)
            book = Book.objects.get(id=book_id)

            if not book.is_available:
                raise serializers.ValidationError({'error': 'Book is not available'})

            # Rule: Maximum books borrowed at once
            active_borrows = BorrowingTransaction.objects.filter(borrower=borrower, returned_date__isnull=True).count()
            max_borrow_limit = getattr(settings, 'MAX_BORROW_LIMIT', 5)
            if active_borrows >= max_borrow_limit:
                raise serializers.ValidationError(
                    {'error': f'Borrower has reached the maximum borrowing limit ({max_borrow_limit})'})

            # Borrowing logic
            borrow_days = getattr(settings, 'BORROW_DAYS', 14)
            due_date = date.today() + timedelta(days=borrow_days)
            BorrowingTransaction.objects.create(borrower=borrower, book=book, due_date=due_date)
            book.is_available = False
            book.save()

            # Notify next reservation
            reservations = Reservation.objects.filter(book=book, notified=False).order_by('created_at')
            if reservations.exists():
                next_reservation = reservations.first()
                next_reservation.notified = True
                next_reservation.save()

            return Response({'success': f'Book "{book.title}" borrowed successfully'}, status=status.HTTP_200_OK)

        except Borrower.DoesNotExist:
            raise serializers.ValidationError({'error': 'Borrower not found'})
        except Book.DoesNotExist:
            raise serializers.ValidationError({'error': 'Book not found'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], url_path='return')
    def return_book(self, request, pk=None):
        try:
            transaction = BorrowingTransaction.objects.get(id=pk, returned_date__isnull=True)
            transaction.returned_date = date.today()
            transaction.book.is_available = True
            transaction.book.save()
            transaction.save()

            return Response({'success': f'Book "{transaction.book.title}" returned successfully'},
                            status=status.HTTP_200_OK)
        except BorrowingTransaction.DoesNotExist:
            return Response({'error': 'Active borrowing transaction not found'}, status=status.HTTP_400_BAD_REQUEST)


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    authentication_classes = [JWTAuthentication]


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    authentication_classes = [JWTAuthentication]
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


class ReportViewSet(ViewSet):
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