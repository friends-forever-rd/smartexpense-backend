"""
Test data for sync push and pull. Use for manual testing, fixtures, or integration tests.
All UUIDs and timestamps are consistent so push payload references (e.g. book_id) are valid.
"""

# Fixed UUIDs for references across tables
BOOK_ID = "11111111-1111-4111-a111-111111111111"
ACCOUNT_ID = "22222222-2222-4222-a222-222222222222"
CATEGORY_INCOME_ID = "33333333-3333-4333-a333-333333333331"
CATEGORY_EXPENSE_ID = "33333333-3333-4333-a333-333333333332"
PAYMENT_MODE_ID = "44444444-4444-4444-a444-444444444444"
TRANSACTION_ID = "55555555-5555-4555-a555-555555555555"

DEVICE_ID = "test-device-001"
BASE_TIME = "2025-02-07T10:00:00+00:00"
BASE_TIME_2 = "2025-02-07T12:00:00+00:00"

# ---- PUSH: request body for POST /sync/push (or for bulk_upsert input) ----
# Records must have id and updated_at; use ISO8601 for datetimes, strings for UUIDs.
PUSH_PAYLOAD = {
    "device_id": DEVICE_ID,
    "books": [
        {
            "id": BOOK_ID,
            "device_id": DEVICE_ID,
            "name": "My Household",
            "created_at": BASE_TIME,
            "updated_at": BASE_TIME,
            "is_deleted": False,
        }
    ],
    "accounts": [
        {
            "id": ACCOUNT_ID,
            "device_id": DEVICE_ID,
            "book_id": BOOK_ID,
            "name": "Cash",
            "account_type": "cash",
            "currency_code": "INR",
            "created_at": BASE_TIME,
            "updated_at": BASE_TIME,
            "is_deleted": False,
        }
    ],
    "categories": [
        {
            "id": CATEGORY_INCOME_ID,
            "device_id": DEVICE_ID,
            "book_id": BOOK_ID,
            "parent_id": None,
            "name": "Salary",
            "category_type": "income",
            "created_at": BASE_TIME,
            "updated_at": BASE_TIME,
            "is_deleted": False,
        },
        {
            "id": CATEGORY_EXPENSE_ID,
            "device_id": DEVICE_ID,
            "book_id": BOOK_ID,
            "parent_id": None,
            "name": "Food",
            "category_type": "expense",
            "created_at": BASE_TIME,
            "updated_at": BASE_TIME,
            "is_deleted": False,
        },
    ],
    "payment_modes": [
        {
            "id": PAYMENT_MODE_ID,
            "device_id": DEVICE_ID,
            "book_id": BOOK_ID,
            "name": "Cash",
            "created_at": BASE_TIME,
            "updated_at": BASE_TIME,
            "is_deleted": False,
        }
    ],
    "transactions": [
        {
            "id": TRANSACTION_ID,
            "device_id": DEVICE_ID,
            "book_id": BOOK_ID,
            "account_id": ACCOUNT_ID,
            "category_id": CATEGORY_EXPENSE_ID,
            "payment_mode_id": PAYMENT_MODE_ID,
            "amount": "-150.00",
            "transaction_date": "2025-02-07T09:30:00+00:00",
            "note": "Groceries",
            "created_at": BASE_TIME,
            "updated_at": BASE_TIME_2,
            "is_deleted": False,
        }
    ],
}

# ---- PULL: example response shape from GET /sync/pull?device_id=... ----
# UUIDs as strings, DateTime as ISO8601, Date as YYYY-MM-DD, server_time included.
PULL_RESPONSE_SAMPLE = {
    "books": [
        {
            "id": BOOK_ID,
            "device_id": DEVICE_ID,
            "name": "My Household",
            "created_at": "2025-02-07T10:00:00+00:00",
            "updated_at": "2025-02-07T10:00:00+00:00",
            "is_deleted": False,
        }
    ],
    "accounts": [
        {
            "id": ACCOUNT_ID,
            "device_id": DEVICE_ID,
            "book_id": BOOK_ID,
            "name": "Cash",
            "account_type": "cash",
            "currency_code": "INR",
            "created_at": "2025-02-07T10:00:00+00:00",
            "updated_at": "2025-02-07T10:00:00+00:00",
            "is_deleted": False,
        }
    ],
    "categories": [
        {
            "id": CATEGORY_INCOME_ID,
            "device_id": DEVICE_ID,
            "book_id": BOOK_ID,
            "parent_id": None,
            "name": "Salary",
            "category_type": "income",
            "created_at": "2025-02-07T10:00:00+00:00",
            "updated_at": "2025-02-07T10:00:00+00:00",
            "is_deleted": False,
        },
        {
            "id": CATEGORY_EXPENSE_ID,
            "device_id": DEVICE_ID,
            "book_id": BOOK_ID,
            "parent_id": None,
            "name": "Food",
            "category_type": "expense",
            "created_at": "2025-02-07T10:00:00+00:00",
            "updated_at": "2025-02-07T10:00:00+00:00",
            "is_deleted": False,
        },
    ],
    "payment_modes": [
        {
            "id": PAYMENT_MODE_ID,
            "device_id": DEVICE_ID,
            "book_id": BOOK_ID,
            "name": "Cash",
            "created_at": "2025-02-07T10:00:00+00:00",
            "updated_at": "2025-02-07T10:00:00+00:00",
            "is_deleted": False,
        }
    ],
    "transactions": [
        {
            "id": TRANSACTION_ID,
            "device_id": DEVICE_ID,
            "book_id": BOOK_ID,
            "account_id": ACCOUNT_ID,
            "category_id": CATEGORY_EXPENSE_ID,
            "payment_mode_id": PAYMENT_MODE_ID,
            "amount": "-150.00",
            "transaction_date": "2025-02-07T09:30:00+00:00",
            "note": "Groceries",
            "created_at": "2025-02-07T10:00:00+00:00",
            "updated_at": "2025-02-07T12:00:00+00:00",
            "is_deleted": False,
        }
    ],
    "server_time": "2025-02-07T12:30:00+00:00",
}

# ---- Minimal push (single book, no relations) for quick tests ----
PUSH_PAYLOAD_MINIMAL = {
    "device_id": "minimal-device",
    "books": [
        {
            "id": "aaaaaaaa-aaaa-4aaa-aaaa-aaaaaaaaaaaa",
            "device_id": "minimal-device",
            "name": "Test Book",
            "created_at": "2025-02-07T00:00:00Z",
            "updated_at": "2025-02-07T00:00:00Z",
            "is_deleted": False,
        }
    ],
    "accounts": [],
    "categories": [],
    "payment_modes": [],
    "transactions": [],
}

# ---- Soft-deleted record example (for push) ----
PUSH_PAYLOAD_WITH_DELETED = {
    "device_id": DEVICE_ID,
    "books": [
        {
            "id": BOOK_ID,
            "device_id": DEVICE_ID,
            "name": "My Household",
            "created_at": BASE_TIME,
            "updated_at": BASE_TIME_2,
            "is_deleted": True,
        }
    ],
    "accounts": [],
    "categories": [],
    "payment_modes": [],
    "transactions": [],
}
