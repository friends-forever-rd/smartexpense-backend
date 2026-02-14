# Serializers for pull and push. id is optional on push (omit for new records).

from rest_framework import serializers
from .models import Book, Account, Category, PaymentMode, Transaction


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = [
            "id", "device_id", "name",
            "created_at", "updated_at", "is_deleted", "status",
        ]
        extra_kwargs = {"id": {"required": False}}


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = [
            "id", "device_id", "book_id", "name", "account_type", "currency_code",
            "created_at", "updated_at", "is_deleted", "status",
        ]
        extra_kwargs = {"id": {"required": False}}


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id", "device_id", "book_id", "parent_id", "name", "category_type",
            "created_at", "updated_at", "is_deleted", "status",
        ]
        extra_kwargs = {"id": {"required": False}}


class PaymentModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMode
        fields = [
            "id", "device_id", "book_id", "name",
            "created_at", "updated_at", "is_deleted", "status",
        ]
        extra_kwargs = {"id": {"required": False}}


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            "id", "device_id", "book_id", "account_id", "category_id", "payment_mode_id",
            "amount", "transaction_date", "note",
            "created_at", "updated_at", "is_deleted", "status",
        ]
        extra_kwargs = {"id": {"required": False}}