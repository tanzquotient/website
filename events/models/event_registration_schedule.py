from django.db import models
from django.db.models import ForeignKey, CharField, DateTimeField, BooleanField
from django.utils import timezone
from reversion import revisions as reversion
from django_celery_beat.models import ClockedSchedule, PeriodicTask
import json


@reversion.register()
class EventRegistrationSchedule(models.Model):
    class Action(models.TextChoices):
        ENABLE = "enable", "Enable registration"
        DISABLE = "disable", "Disable registration"

    event = ForeignKey(
        "Event",
        related_name="registration_schedules",
        on_delete=models.CASCADE,
    )
    action = CharField(
        max_length=10,
        choices=Action.choices,
        help_text=(
            "Choose 'Enable registration' to open registrations or "
            "'Disable registration' to close them at the scheduled time."
        ),
    )
    run_at = DateTimeField(
        help_text="Date and time when the chosen action will be executed (timezone-aware).",
    )
    executed = BooleanField(
        default=False,
        help_text="Automatically marked when the scheduled task executed successfully.",
    )

    def save(self, *args, **kwargs):
        skip_sync = kwargs.pop("_skip_sync", False)
        super().save(*args, **kwargs)  # ensure we have an id
        if not skip_sync:
            self._sync_periodic_task()

    def delete(self, *args, **kwargs):
        self._delete_periodic_task()
        super().delete(*args, **kwargs)

    def _sync_periodic_task(self):
        # remove any existing periodic tasks for this schedule (name prefixed by id)
        task_name = f"events:registration:{self.id}"
        PeriodicTask.objects.filter(name=task_name).delete()

        run_at = self.run_at
        if timezone.is_naive(run_at):
            run_at = timezone.make_aware(run_at, timezone.get_current_timezone())

        clocked, _ = ClockedSchedule.objects.get_or_create(clocked_time=run_at)

        task_name = "events.tasks.toggle_event_registration"
        name = f"events:registration:{self.id}"

        args = json.dumps([self.id, self.event_id, self.action])

        PeriodicTask.objects.update_or_create(
            name=name,
            defaults={
                "task": task_name,
                "clocked": clocked,
                "one_off": True,
                "enabled": True,
                "args": args,
            },
        )

        # reset executed flag when (re)scheduling
        if self.executed:
            self.__class__.objects.filter(pk=self.pk).update(executed=False)

    def _delete_periodic_task(self):
        task_name = f"events:registration:{self.id}"
        PeriodicTask.objects.filter(name=task_name).delete()

    def __str__(self):
        return f"{self.get_action_display()} at {self.run_at} for {self.event_id}"
