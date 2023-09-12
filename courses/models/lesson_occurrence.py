from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(frozen=True, order=True)
class LessonOccurrence:
    start: datetime
    end: datetime

    @property
    def duration(self) -> timedelta:
        return self.end - self.start
