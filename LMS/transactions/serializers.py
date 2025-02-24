from rest_framework import serializers
from .models import *

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
