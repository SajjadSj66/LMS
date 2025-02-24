from rest_framework import viewsets, status
from .models import *
from .serializers import *
from users.permission import *
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from library.tasks import *
from rest_framework.response import Response
from django.conf import settings


# Create your views here.
class BorrowingTransactionViewSet(viewsets.ModelViewSet):
    queryset = BorrowingTransaction.objects.all()
    serializer_class = BorrowingTransactionSerializer

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
