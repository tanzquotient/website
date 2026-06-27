from django.core.exceptions import ValidationError


def validate_amount(cleaned_data: dict) -> int:
    amount = cleaned_data.get("amount")
    if amount and amount < 0:
        raise ValidationError("The amount must be non-negative")
    return amount
