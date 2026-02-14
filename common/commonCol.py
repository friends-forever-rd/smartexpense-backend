import uuid
from django.db import models
from common.choices import status_choices

class CommonColMixin(models.Model):
    """Abstract base for common columns. No business logic, no signals."""
    device_id = models.CharField(max_length=255, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    status = models.CharField(max_length=50, choices=status_choices, default='ACTIVE')
    class Meta:
        abstract = True


# Alias for root expense app / sync (uses common columns + UUID id elsewhere)
SyncBaseModel = CommonColMixin
