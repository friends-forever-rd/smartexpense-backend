# Serializers for pull and push. On push, client sends "id" (treated as app_id); required for upsert.
# Response: "id" is app_id (UUID); numeric pk not exposed; FKs returned as related app_id.

from rest_framework import serializers
from .models import Book, Account, Category, PaymentMode, Transaction


class AppIdRelatedField(serializers.Field):
    """Accepts app_id (UUID/str) in input; resolves to model instance via device_id; outputs app_id in response."""
    def __init__(self, model, allow_null=False, **kwargs):
        self.related_model = model
        self.allow_null = allow_null
        super().__init__(allow_null=allow_null, **kwargs)

    def to_representation(self, value):
        return str(value.app_id) if value else None

    def to_internal_value(self, data):
        if data is None or data == "":
            if self.allow_null:
                return None
            raise serializers.ValidationError("This field may not be null.")
        device_id = (self.root.context or {}).get("device_id")
        if not device_id:
            raise serializers.ValidationError("device_id required for relation resolution.")
        obj = self.related_model.objects.filter(device_id=device_id, app_id=data).first()
        if not obj:
            raise serializers.ValidationError("Not found for given app_id.")
        return obj


def _repr_id_as_app_id(instance, data):
    """Set response 'id' from app_id; do not expose numeric id. FK fields already output app_id via AppIdRelatedField."""
    data["id"] = data.pop("app_id", None)
    return data


class BookSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(required=False, allow_null=True)
    updated_at = serializers.DateTimeField(required=True)

    class Meta:
        model = Book
        fields = [
            "app_id", "device_id", "name",
            "created_at", "updated_at", "is_deleted", "status",
        ]
        extra_kwargs = {
            "app_id": {"required": False},
            "device_id": {"read_only": True},
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return _repr_id_as_app_id(instance, data)


class AccountSerializer(serializers.ModelSerializer):
    book_id = AppIdRelatedField(model=Book)
    created_at = serializers.DateTimeField(required=False, allow_null=True)
    updated_at = serializers.DateTimeField(required=True)

    class Meta:
        model = Account
        fields = [
            "app_id", "device_id", "book_id", "name", "account_type", "currency_code",
            "created_at", "updated_at", "is_deleted", "status",
        ]
        extra_kwargs = {
            "app_id": {"required": False},
            "device_id": {"read_only": True},
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return _repr_id_as_app_id(instance, data)


class CategorySerializer(serializers.ModelSerializer):
    book_id = AppIdRelatedField(model=Book)
    parent_id = AppIdRelatedField(model=Category, allow_null=True)
    created_at = serializers.DateTimeField(required=False, allow_null=True)
    updated_at = serializers.DateTimeField(required=True)

    class Meta:
        model = Category
        fields = [
            "app_id", "device_id", "book_id", "parent_id", "name", "category_type",
            "created_at", "updated_at", "is_deleted", "status",
        ]
        extra_kwargs = {
            "app_id": {"required": False},
            "device_id": {"read_only": True},
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return _repr_id_as_app_id(instance, data)


class PaymentModeSerializer(serializers.ModelSerializer):
    book_id = AppIdRelatedField(model=Book)
    created_at = serializers.DateTimeField(required=False, allow_null=True)
    updated_at = serializers.DateTimeField(required=True)

    class Meta:
        model = PaymentMode
        fields = [
            "app_id", "device_id", "book_id", "name",
            "created_at", "updated_at", "is_deleted", "status",
        ]
        extra_kwargs = {
            "app_id": {"required": False},
            "device_id": {"read_only": True},
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return _repr_id_as_app_id(instance, data)


class TransactionSerializer(serializers.ModelSerializer):
    book_id = AppIdRelatedField(model=Book)
    account_id = AppIdRelatedField(model=Account)
    category_id = AppIdRelatedField(model=Category)
    payment_mode_id = AppIdRelatedField(model=PaymentMode)
    created_at = serializers.DateTimeField(required=False, allow_null=True)
    updated_at = serializers.DateTimeField(required=True)

    class Meta:
        model = Transaction
        fields = [
            "app_id", "device_id", "book_id", "account_id", "category_id", "payment_mode_id",
            "amount", "transaction_date", "note",
            "created_at", "updated_at", "is_deleted", "status",
        ]
        extra_kwargs = {
            "app_id": {"required": False},
            "device_id": {"read_only": True},
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return _repr_id_as_app_id(instance, data)
