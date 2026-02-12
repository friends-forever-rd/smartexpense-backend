"""
GET /sync/pull and POST /sync/push for offline-first sync.
No authentication, no serializers, no pagination.
"""
from datetime import date, datetime
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from expense.models import Account, Book, Category, PaymentMode, Transaction
from sync.utils.bulk_upsert import bulk_upsert


def _parse_since(value):
    """Parse ISO8601 to timezone-aware datetime. Return None if missing or invalid."""
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    dt = parse_datetime(str(value).strip().replace("Z", "+00:00"))
    if dt is None:
        return None
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt)
    return dt


def _value_to_json(value):
    """Convert a field value for JSON: UUID -> str, DateTime -> ISO8601, Date -> YYYY-MM-DD."""
    if value is None:
        return None
    if hasattr(value, "hex"):  # UUID
        return str(value)
    if hasattr(value, "isoformat"):  # date, datetime
        if isinstance(value, datetime):
            return timezone.make_aware(value).isoformat() if timezone.is_naive(value) else value.isoformat()
        if isinstance(value, date):
            return value.strftime("%Y-%m-%d")
        return value.isoformat()
    if hasattr(value, "quantize"):  # Decimal
        return str(value)
    return value


def _instance_to_dict(instance):
    """Turn a model instance into a dict with UUID/DateTime/Date converted for JSON."""
    return {
        f.name: _value_to_json(getattr(instance, f.name))
        for f in instance._meta.get_fields()
        if getattr(f, "column", None) and not f.many_to_many and not f.one_to_many
    }


def _fetch_table(model, device_id, since):
    """Fetch records for model filtered by device_id, optionally updated_at > since. Include soft-deleted."""
    qs = model.objects.filter(device_id=device_id)
    if since is not None:
        qs = qs.filter(updated_at__gt=since)
    return [_instance_to_dict(obj) for obj in qs]


class PullView(APIView):
    """GET /sync/pull?device_id=...&since=... (since optional ISO8601)."""

    authentication_classes = []
    permission_classes = []

    def get(self, request):
        device_id = request.query_params.get("device_id")
        if not device_id or (isinstance(device_id, str) and not device_id.strip()):
            return Response(
                {"error": "device_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        device_id = device_id.strip()

        since = _parse_since(request.query_params.get("since"))

        data = {
            "accounts": _fetch_table(Account, device_id, since),
            "books": _fetch_table(Book, device_id, since),
            "categories": _fetch_table(Category, device_id, since),
            "payment_modes": _fetch_table(PaymentMode, device_id, since),
            "transactions": _fetch_table(Transaction, device_id, since),
            "server_time": timezone.now().isoformat(),
        }
        return Response(data)


class PushView(APIView):
    """POST /sync/push with body: { device_id, books, accounts, categories, payment_modes, transactions }."""

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        body = request.data if getattr(request, "data", None) is not None else {}
        if not isinstance(body, dict):
            return Response(
                {"error": "Request body must be JSON object"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        device_id = body.get("device_id")
        if not device_id or (isinstance(device_id, str) and not device_id.strip()):
            return Response(
                {"error": "device_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        device_id = device_id.strip()

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

        bulk_upsert(Book, books, device_id)
        bulk_upsert(Account, accounts, device_id)
        bulk_upsert(Category, categories, device_id)
        bulk_upsert(PaymentMode, payment_modes, device_id)
        bulk_upsert(Transaction, transactions, device_id)

        return Response({"ok": True}, status=status.HTTP_200_OK)
