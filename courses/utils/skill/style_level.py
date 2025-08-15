from dataclasses import dataclass

from courses.models import Style


@dataclass(frozen=True, kw_only=True, unsafe_hash=True)
class StyleLevel:
    style: Style
    level: int
