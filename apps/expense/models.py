from django.db import models
from common.commonCol import CommonColMixin
# Create your models here.
class Book(CommonColMixin, models.Model):
    app_id = models.TextField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'expense_book'
        constraints = [
            models.UniqueConstraint(
                fields=['device_id', 'app_id'],
                name='unique_book_device_appid'
            )
        ]

class Account(CommonColMixin, models.Model):
    app_id = models.TextField(max_length=255, null=True, blank=True)
    book_id = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='accounts')
    name = models.CharField(max_length=255)
    account_type = models.CharField(max_length=50)
    currency_code = models.CharField(max_length=10, default='INR')

    class Meta:
        db_table = 'expense_account'
        constraints = [
            models.UniqueConstraint(
                fields=['device_id', 'app_id'],
                name='unique_account_device_appid'
            )
        ]

class Category(CommonColMixin, models.Model):
    app_id = models.TextField(max_length=255, null=True, blank=True)
    book_id = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='categories')
    parent_id = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255)
    category_type = models.CharField(max_length=20)

    class Meta:
        db_table = 'expense_category'
        constraints = [
            models.UniqueConstraint(
                fields=['device_id', 'app_id'],
                name='unique_category_device_appid'
            )
        ]

class PaymentMode(CommonColMixin, models.Model):
    app_id = models.TextField(max_length=255, null=True, blank=True)
    book_id = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='payment_modes')
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'expense_paymentmode'
        constraints = [
            models.UniqueConstraint(
                fields=['device_id', 'app_id'],
                name='unique_paymentmode_device_appid'
            )
        ]

class Transaction(CommonColMixin, models.Model):
    app_id = models.TextField(max_length=255, null=True, blank=True)
    book_id = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='transactions_book')
    account_id = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions_account')
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='transactions_category')
    payment_mode_id = models.ForeignKey(PaymentMode, on_delete=models.CASCADE, related_name='transactions_payment_mode')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    transaction_date = models.DateTimeField()
    note = models.TextField(blank=True)

    class Meta:
        db_table = 'expense_transaction'
        constraints = [
            models.UniqueConstraint(
                fields=['device_id', 'app_id'],
                name='unique_transaction_device_appid'
            )
        ]