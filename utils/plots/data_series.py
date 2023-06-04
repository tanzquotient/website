from decimal import Decimal
from typing import Optional, Union


class DataSeries:
    def __init__(
        self,
        name: str,
        values: list[Union[float, int, Decimal]],
        color: Optional[str] = None,
    ) -> None:
        self.name: str = name
        self.values: list[Union[float, int, Decimal]] = values
        self.color: Optional[str] = color
