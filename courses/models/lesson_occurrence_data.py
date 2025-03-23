from dataclasses import dataclass
from datetime import datetime, timedelta

from courses.models import Room


@dataclass(frozen=True, order=True)
class LessonOccurrenceData:
    start: datetime
    end: datetime
    room: Room | None

    @property
    def duration(self) -> timedelta:
        return self.end - self.start
