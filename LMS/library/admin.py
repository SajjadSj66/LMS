from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Author)
admin.site.register(Book)
admin.site.register(Borrower)
admin.site.register(BorrowingTransaction)
admin.site.register(Reservation)
admin.site.register(Review)