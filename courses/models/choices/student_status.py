class StudentStatus:
    ETH = 'eth'
    UNI = 'uni'
    PH = 'ph'
    OTHER = 'other'
    NO = 'no'

    TEXT = {
        ETH: 'ETH',
        UNI: 'UZH',
        PH: 'PH',
        OTHER: 'Other',
        NO: 'Not a student',
    }

    CHOICES = (
        (ETH, TEXT[ETH]),
        (UNI, TEXT[UNI]),
        (PH, TEXT[PH]),
        (OTHER, TEXT[OTHER]),
        (NO, TEXT[NO])
    )

    UNIVERSITY_CHOICES = (
        (ETH, TEXT[ETH]),
        (UNI, TEXT[UNI]),
        (PH, TEXT[PH]),
        (OTHER, TEXT[OTHER]),
    )

    STUDENTS = [ETH, UNI, PH, OTHER]
