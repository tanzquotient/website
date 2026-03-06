from celery import shared_task
from django_celery_beat.models import PeriodicTask
from reversion import revisions
import logging

from events.models import Event, EventRegistrationSchedule

logger = logging.getLogger(__name__)


@shared_task
def toggle_event_registration(schedule_id, event_id, action):
    try:
        event = Event.objects.get(pk=event_id)
    except Event.DoesNotExist:
        logger.warning("Event %s does not exist (toggle registration)", event_id)
        PeriodicTask.objects.filter(name=f"events:registration:{schedule_id}").delete()
        return

    # determine boolean from action string (compare to the TextChoices value)
    try:
        enable = str(action) == EventRegistrationSchedule.Action.ENABLE.value
    except Exception:
        enable = str(action) == "enable"

    try:
        with revisions.create_revision():
            event.registration_enabled = enable
            event.save(update_fields=["registration_enabled"])
            revisions.set_comment(
                f"Scheduled toggle by schedule {schedule_id}: set registration_enabled to {enable} for event {event_id}"
            )
    except Exception:
        event.registration_enabled = enable
        event.save(update_fields=["registration_enabled"])

    try:
        schedule = EventRegistrationSchedule.objects.get(pk=schedule_id)
    except EventRegistrationSchedule.DoesNotExist:
        PeriodicTask.objects.filter(name=f"events:registration:{schedule_id}").delete()
        return

    try:
        schedule.executed = True
        with revisions.create_revision():
            # avoid re-syncing the periodic task when saving
            schedule.save(update_fields=["executed"], _skip_sync=True)
            revisions.set_comment(
                f"Executed by Celery: set registration_enabled to {enable} for event {event_id} (schedule {schedule_id})"
            )
    except Exception:
        schedule.__class__.objects.filter(pk=schedule.pk).update(executed=True)

    PeriodicTask.objects.filter(name=f"events:registration:{schedule_id}").delete()
