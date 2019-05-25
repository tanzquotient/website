class CourseSubscriptionType:

    REGULAR = 'regular'
    OPEN_CLASS = 'open_class'
    EXTERNAL = 'external'

    CHOICES = (
        (REGULAR, 'Regular (internal, with subscription)'),
        (OPEN_CLASS, 'Open class (no subscription needed)'),
        (EXTERNAL, 'External (offered by partner of TQ)'),
    )
