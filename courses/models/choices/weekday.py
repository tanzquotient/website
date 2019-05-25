class Weekday:
    MONDAY = 'mon'
    TUESDAY = 'tue'
    WEDNESDAY = 'wed'
    THURSDAY = 'thu'
    FRIDAY = 'fri'
    SATURDAY = 'sat'
    SUNDAY = 'sun'

    WEEKEND = [SATURDAY, SUNDAY]

    CHOICES = (
        (MONDAY, 'Monday'),
        (TUESDAY, 'Tuesday'),
        (WEDNESDAY, 'Wednesday'),
        (THURSDAY, 'Thursday'),
        (FRIDAY, 'Friday'),
        (SATURDAY, 'Saturday'),
        (SUNDAY, 'Sunday')
    )

    NUMBERS = {
        MONDAY: 0,
        TUESDAY: 1,
        WEDNESDAY: 2,
        THURSDAY: 3,
        FRIDAY: 4,
        SATURDAY: 5,
        SUNDAY: 6
    }
    NUMBER_2_SLUG = {number: slug for slug, number in NUMBERS.items()}

    WEEKDAYS_TRANSLATIONS_DE = {
        MONDAY: 'Montag',
        TUESDAY: 'Dienstag',
        WEDNESDAY: 'Mittwoch',
        THURSDAY: 'Donnerstag',
        FRIDAY: 'Freitag',
        SATURDAY: 'Samstag',
        SUNDAY: 'Sonntag'
    }
