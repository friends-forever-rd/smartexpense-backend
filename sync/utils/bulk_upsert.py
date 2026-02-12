"""
Bulk upsert utility for offline-first sync. Last-write-wins by updated_at.
No save(), serializers, signals, or business logic. Does not raise on partial failure.
"""
import uuid
from django.db import models
from django.utils import timezone
from django.utils.dateparse import parse_datetime


def _parse_dt(value):
    """Parse ISO string to timezone-aware datetime. Return None on failure."""
    if value is None:
        return None
    if hasattr(value, "isoformat"):
        dt = value
    else:
        dt = parse_datetime(str(value).replace("Z", "+00:00"))
    if dt is None:
        return None
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt)
    return dt


def _value_for_field(model, field_name, value):
    """Coerce value for model field (e.g. ISO string -> datetime for DateTimeField)."""
    if value is None:
        return value
    try:
        field = model._meta.get_field(field_name)
        if isinstance(field, models.DateTimeField):
            return _parse_dt(value)
        if isinstance(field, models.UUIDField) and isinstance(value, str):
            return uuid.UUID(value)
    except Exception:
        pass
    return value


def _record_to_kwargs(model, record, device_id, *, include_id=True):
    """Build kwargs for model from record dict. Only includes model field names."""
    kwargs = {}
    for f in model._meta.get_fields():
        if not getattr(f, "column", None) or f.many_to_many or f.one_to_many:
            continue
        name = f.name
        if name == "id" and not include_id:
            continue
        if name in record:
            val = _value_for_field(model, name, record[name])
            if val is not None or f.null:
                kwargs[name] = val
    kwargs["device_id"] = device_id
    return kwargs


def bulk_upsert(model, records, device_id):
    """
    Upsert records for the given model and device_id.
    Match by id; last-write-wins by updated_at. Respect is_deleted.
    Uses bulk_create for new rows and bulk_update for existing.
    Ignores records missing id or updated_at. Does not raise on partial failure.
    """
    try:
        valid = []
        for r in records:
            if not r or not isinstance(r, dict):
                continue
            id_val = r.get("id")
            updated_at_val = r.get("updated_at")
            if id_val is None or updated_at_val is None:
                continue
            parsed_at = _parse_dt(updated_at_val)
            if parsed_at is None:
                continue
            valid.append((r, parsed_at))

        if not valid:
            return

        ids = [r[0]["id"] for r in valid]
        existing_qs = model.objects.filter(device_id=device_id, id__in=ids)
        existing_map = {str(obj.id): obj for obj in existing_qs}

        to_insert = []
        to_update = []

        for record, incoming_updated_at in valid:
            rid = record["id"]
            rid_str = str(rid) if not isinstance(rid, str) else rid
            existing = existing_map.get(rid_str)

            if existing is None:
                to_insert.append((record, incoming_updated_at))
            else:
                existing_at = existing.updated_at
                if timezone.is_naive(existing_at):
                    existing_at = timezone.make_aware(existing_at)
                if incoming_updated_at >= existing_at:
                    to_update.append((existing, record))

        if to_insert:
            created_at_field = "created_at"
            objs = []
            for record, _ in to_insert:
                kwargs = _record_to_kwargs(model, record, device_id, include_id=True)
                created_val = kwargs.get(created_at_field)
                if created_val is None:
                    kwargs[created_at_field] = kwargs.get("updated_at")
                if "id" in kwargs and isinstance(kwargs["id"], str):
                    kwargs["id"] = uuid.UUID(kwargs["id"])
                objs.append(model(**kwargs))
            if objs:
                model.objects.bulk_create(objs)

        if to_update:
            all_update_fields = set()
            for existing, record in to_update:
                for f in model._meta.get_fields():
                    if not getattr(f, "column", None) or f.many_to_many or f.one_to_many or f.name == "id":
                        continue
                    if f.name not in record:
                        continue
                    val = _value_for_field(model, f.name, record[f.name])
                    if f.name == "created_at" and val is None:
                        val = getattr(existing, "created_at", None)
                    setattr(existing, f.name, val)
                    all_update_fields.add(f.name)
                existing.device_id = device_id
                all_update_fields.add("device_id")
            model.objects.bulk_update([o for o, _ in to_update], list(all_update_fields))

    except Exception:
        pass
