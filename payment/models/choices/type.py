class Type:
    SUBSCRIPTION_PAYMENT = 'subscription_payment'
    SUBSCRIPTION_PAYMENT_TO_REIMBURSE = 'subscription_payment_to_reimburse'
    COURSE_PAYMENT_TRANSFER = 'course_payment_transfer'
    IRRELEVANT = 'irrelevant'
    UNKNOWN = 'unknown'


    CHOICES = (
        (SUBSCRIPTION_PAYMENT, 'subscription payment'),
        (SUBSCRIPTION_PAYMENT_TO_REIMBURSE, 'subscription payment (to reimburse)'),
        (COURSE_PAYMENT_TRANSFER, 'course payment transfer'),
        (IRRELEVANT, 'irrelevant'),
        (UNKNOWN, 'unknown')
    )