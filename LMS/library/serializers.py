from rest_framework import serializers

from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']


class AuthorSerializer(serializers.ModelSerializer):
    books = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Author
        fields = '__all__'


class BookSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = '__all__'


class BorrowerSerializer(serializers.ModelSerializer):
    borrowing_history = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Borrower
        fields = '__all__'


class BorrowingTransactionSerializer(serializers.ModelSerializer):
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = BorrowingTransaction
        fields = '__all__'

    def get_is_overdue(self, obj):
        return obj.is_overdue()


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'
