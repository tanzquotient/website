class PaymentMethod:
    COUNTER = 'counter'
    COURSE = 'course'
    ONLINE = 'online'
    VOUCHER = 'voucher'

    CHOICES = (
        (COUNTER, 'counter'),
        (COURSE, 'course'),
        (ONLINE, 'online'),
        (VOUCHER, 'voucher')
    )
