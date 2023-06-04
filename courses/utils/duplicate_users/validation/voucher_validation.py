from django.core.exceptions import ValidationError


def validate_amount_and_percentage(cleaned_data: dict) -> dict:
    amount = cleaned_data.get("amount")
    percentage = cleaned_data.get("percentage")

    if not amount and not percentage:
        raise ValidationError("You need to set either the amount or percentage.")
    if amount and percentage:
        raise ValidationError("You are not allowed to set both amount and percentage.")

    return cleaned_data


def validate_amount(cleaned_data: dict) -> int:
    amount = cleaned_data.get("amount")
    if amount and amount < 0:
        raise ValidationError("The amount must be non-negative")
    return amount


def validate_percentage(cleaned_data: dict) -> int:
    percentage = cleaned_data.get("percentage")
    if percentage and (percentage < 0 or percentage > 100):
        raise ValidationError("The percentage must be between 0 and 100")
    return percentage
