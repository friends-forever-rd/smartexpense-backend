# Pull: GET ?device_id=xxx&since=optional-iso-date
# Push: POST body with device_id and lists: books, accounts, categories, payment_modes, transactions

from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.views import APIView

from common.response import success_response, error_response
from .models import Book, Account, Category, PaymentMode, Transaction
from .serializers import (
    BookSerializer,
    AccountSerializer,
    CategorySerializer,
    PaymentModeSerializer,
    TransactionSerializer,
)


def parse_dt(value):
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    if hasattr(value, "isoformat"):
        dt = value
    else:
        dt = parse_datetime(str(value).strip().replace("Z", "+00:00"))
    if dt is None:
        return None
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt)
    return dt


class PullView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        device_id = (request.query_params.get("device_id") or "").strip()
        if not device_id:
            return error_response("device_id is required", status.HTTP_400_BAD_REQUEST)

        since = parse_dt(request.query_params.get("since"))

        # Get all data for this device (and optionally only rows updated after since)
        books = Book.objects.filter(device_id=device_id)
        if since:
            books = books.filter(updated_at__gt=since)
        books = BookSerializer(books, many=True).data

        accounts = Account.objects.filter(device_id=device_id)
        if since:
            accounts = accounts.filter(updated_at__gt=since)
        accounts = AccountSerializer(accounts, many=True).data

        categories = Category.objects.filter(device_id=device_id)
        if since:
            categories = categories.filter(updated_at__gt=since)
        categories = CategorySerializer(categories, many=True).data

        payment_modes = PaymentMode.objects.filter(device_id=device_id)
        if since:
            payment_modes = payment_modes.filter(updated_at__gt=since)
        payment_modes = PaymentModeSerializer(payment_modes, many=True).data

        transactions = Transaction.objects.filter(device_id=device_id)
        if since:
            transactions = transactions.filter(updated_at__gt=since)
        transactions = TransactionSerializer(transactions, many=True).data

        data = {
            "books": books,
            "accounts": accounts,
            "categories": categories,
            "payment_modes": payment_modes,
            "transactions": transactions,
            "server_time": timezone.now().isoformat(),
        }
        return success_response(data, 200)


def upsert_list(model, records, device_id, serializer_class, errors_out=None):
    """
    For each record: validate, then create or update.
    Incoming payload "id" is treated as app_id (renamed internally).
    Match is by device_id + app_id only (never by numeric id).
    New records get app_id from payload; backend never generates UUID.
    """
    if errors_out is None:
        errors_out = []
    for idx, record in enumerate(records):
        if not record or not isinstance(record, dict):
            errors_out.append({"index": idx, "error": "empty or invalid record"})
            continue
        # Treat incoming "id" as app_id: rename before validation
        payload = dict(record)
        if "id" in payload:
            payload["app_id"] = payload.pop("id")
        ser = serializer_class(data=payload, context={"device_id": device_id})
        if not ser.is_valid():
            errors_out.append({"index": idx, "errors": ser.errors})
            continue
        data = dict(ser.validated_data)
        payload_app_id = data.get("app_id")
        if payload_app_id is None:
            errors_out.append({"index": idx, "error": "id (app_id) is required"})
            continue
        # updated_at required for conflict resolution
        new_updated = data.get("updated_at")
        if new_updated is None:
            errors_out.append({"index": idx, "error": "updated_at is required"})
            continue
        new_updated = parse_dt(new_updated)
        if new_updated is None:
            errors_out.append({"index": idx, "error": "updated_at must be a valid ISO datetime"})
            continue
        # Match by device_id + app_id only (never numeric id)
        existing = model.objects.filter(device_id=device_id, app_id=payload_app_id).first()
        if existing:
            old_updated = existing.updated_at
            if timezone.is_naive(old_updated):
                old_updated = timezone.make_aware(old_updated)
            if new_updated < old_updated:
                continue
            for key, val in data.items():
                if key not in ("id", "app_id"):
                    setattr(existing, key, val)
            existing.updated_at = new_updated
            existing.save()
        else:
            # Create: set app_id from payload; do not generate UUID
            data.pop("id", None)
            data["device_id"] = device_id
            data["app_id"] = payload_app_id
            data["updated_at"] = new_updated
            if data.get("created_at") is None:
                data["created_at"] = new_updated
            model.objects.create(**data)


class PushView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        body = request.data
        if not isinstance(body, dict):
            return error_response("Body must be JSON object", status.HTTP_400_BAD_REQUEST)

        device_id = (body.get("device_id") or "").strip()
        if not device_id:
            return error_response("device_id is required", status.HTTP_400_BAD_REQUEST)

        books = body.get("books") or []
        accounts = body.get("accounts") or []
        categories = body.get("categories") or []
        payment_modes = body.get("payment_modes") or []
        transactions = body.get("transactions") or []

        if not isinstance(books, list):
            books = []
        if not isinstance(accounts, list):
            accounts = []
        if not isinstance(categories, list):
            categories = []
        if not isinstance(payment_modes, list):
            payment_modes = []
        if not isinstance(transactions, list):
            transactions = []

        all_errors = {}
        upsert_list(Book, books, device_id, BookSerializer, all_errors.setdefault("books", []))
        upsert_list(Account, accounts, device_id, AccountSerializer, all_errors.setdefault("accounts", []))
        upsert_list(Category, categories, device_id, CategorySerializer, all_errors.setdefault("categories", []))
        upsert_list(PaymentMode, payment_modes, device_id, PaymentModeSerializer, all_errors.setdefault("payment_modes", []))
        upsert_list(Transaction, transactions, device_id, TransactionSerializer, all_errors.setdefault("transactions", []))

        data = {"ok": True}
        if any(all_errors.values()):
            data["errors"] = {k: v for k, v in all_errors.items() if v}
        return success_response(data, 200)

