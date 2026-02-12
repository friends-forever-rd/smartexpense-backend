from django.db import models
from common.commonCol import SyncBaseModel


class Book(SyncBaseModel):
    """Book (ledger) - top-level container. No relations."""
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'expense_book'


class Account(SyncBaseModel):
    """Account belongs to a book. UUID reference only."""
    book_id = models.UUIDField(db_index=True)
    name = models.CharField(max_length=255)
    account_type = models.CharField(max_length=50)
    currency_code = models.CharField(max_length=10, default='INR')

    class Meta:
        db_table = 'expense_account'


class Category(SyncBaseModel):
    """Category belongs to a book; optional parent for subcategories."""
    book_id = models.UUIDField(db_index=True)
    parent_id = models.UUIDField(null=True, blank=True, db_index=True)
    name = models.CharField(max_length=255)
    category_type = models.CharField(max_length=20)  # e.g. income, expense

    class Meta:
        db_table = 'expense_category'


class PaymentMode(SyncBaseModel):
    """Payment mode belongs to a book."""
    book_id = models.UUIDField(db_index=True)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'expense_paymentmode'


class Transaction(SyncBaseModel):
    """Transaction references book, account, category, payment_mode by UUID."""
    book_id = models.UUIDField(db_index=True)
    account_id = models.UUIDField(db_index=True)
    category_id = models.UUIDField(db_index=True)
    payment_mode_id = models.UUIDField(db_index=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    transaction_date = models.DateTimeField(db_index=True)
    note = models.TextField(blank=True)

    class Meta:
        db_table = 'expense_transaction'
