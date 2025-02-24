import csv
from datetime import datetime, timedelta
from django.core.files.storage import default_storage
from celery import shared_task
from transactions.models import BorrowingTransaction, Book, Borrower
from django.db.models import Count

# Task 1: Generate Most Borrowed Books Report
@shared_task
def generate_most_borrowed_books_report():
    # Query most borrowed books
    report_data = Book.objects.annotate(borrow_count=Count('BorrowingTransaction')).order_by('-borrow_count')
    file_path = f"reports/most_borrowed_books_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"

    # Write the report to a CSV file
    with default_storage.open(file_path, 'w') as file:
        writer = csv.writer(file)
        writer.writerow(['Book Title', 'Borrow Count'])
        for book in report_data:
            writer.writerow([book.title, book.borrow_count])
    return file_path

# Task 2: Generate Overdue Borrowers Report
@shared_task
def generate_overdue_borrowers_report():
    overdue_date = datetime.now() - timedelta(days=14)  # Books overdue by 14 days
    report_data = BorrowingTransaction.objects.filter(return_date=None, due_date__lt=overdue_date)
    file_path = f"reports/overdue_borrowers_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"

    # Write the report to a CSV file
    with default_storage.open(file_path, 'w') as file:
        writer = csv.writer(file)
        writer.writerow(['Borrower', 'Book Title', 'Due Date'])
        for transaction in report_data:
            writer.writerow([transaction.borrower.username, transaction.book.title, transaction.due_date])
    return file_path

# Task 3: Generate Checked Out Books Report
@shared_task
def generate_checked_out_books_report():
    report_data = BorrowingTransaction.objects.filter(return_date=None)  # Books not yet returned
    file_path = f"reports/checked_out_books_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"

    # Write the report to a CSV file
    with default_storage.open(file_path, 'w') as file:
        writer = csv.writer(file)
        writer.writerow(['Book Title', 'Borrower', 'Due Date'])
        for transaction in report_data:
            writer.writerow([transaction.book.title, transaction.borrower.username, transaction.due_date])
    return file_path
