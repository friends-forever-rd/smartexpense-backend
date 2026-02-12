import uuid
from django.db import models


class SyncBaseModel(models.Model):
    """Abstract base for offline-first sync models. No business logic, no signals."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device_id = models.CharField(max_length=255, db_index=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(db_index=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True
