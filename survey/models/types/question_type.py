class QuestionType:
    SINGLE_CHOICE = 'c'
    SINGLE_CHOICE_WITH_FREE_FORM = 'cf'
    MULTIPLE_CHOICE = 'm'
    MULTIPLE_CHOICE_WITH_FREE_FORM = 'mf'
    SCALE = 's'
    FREE_FORM = 'f'

    CHOICES = ((SINGLE_CHOICE, 'single choice'),
               (SINGLE_CHOICE_WITH_FREE_FORM, 'single choice with free form'),
               (MULTIPLE_CHOICE, 'multiple choice'),
               (MULTIPLE_CHOICE_WITH_FREE_FORM, 'multiple choice with free form'),
               (SCALE, 'scale'),
               (FREE_FORM, 'free form'))
