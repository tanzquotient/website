class PaymentMethod:
    COUNTER = "counter"
    COURSE = "course"
    ONLINE = "online"
    VOUCHER = "voucher"
    PRICE_REDUCTION = "reduction"
    MANUAL = "manual"
    CARD = "card"
    TWINT = "twint"

    CHOICES = (
        (COUNTER, "counter"),
        (COURSE, "course"),
        (ONLINE, "online"),
        (VOUCHER, "voucher"),
        (PRICE_REDUCTION, "price reduction"),
        (MANUAL, "manual"),
        (CARD, "card (Payrexx)"),
        (TWINT, "TWINT (Payrexx)"),
    )
