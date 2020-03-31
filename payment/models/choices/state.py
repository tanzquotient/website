class State:
    NEW = 'new'
    MANUAL = 'manual'
    MATCHED = 'matched'
    PROCESSED = 'processed'
    ARCHIVE = 'archive'

    CHOICES = (
        (NEW, 'new'),
        (MANUAL, 'manual'),
        (MATCHED, 'matched'),
        (PROCESSED, 'processed'),
        (ARCHIVE, 'archive')
    )
