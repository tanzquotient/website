from decimal import Decimal


class DataSeries:
    def __init__(
        self,
        name: str,
        values: list[float | int | Decimal],
        color: str | None = None,
        visible: str | None = None,
    ) -> None:
        self.name: str = name
        self.values: list[float | int | Decimal] = values
        self.color: str | None = color
        self.visible: str | None = visible
