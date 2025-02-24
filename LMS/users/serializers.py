from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']


class BorrowerSerializer(serializers.ModelSerializer):
    borrowing_history = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Borrower
        fields = '__all__'
