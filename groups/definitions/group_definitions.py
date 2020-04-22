from .group_definition import GroupDefinition
from .predicates import *

class GroupDefinitions:

    ALL_TEACHERS = GroupDefinition(name='All teachers', predicate=is_teacher)
    CURRENT_TEACHERS = GroupDefinition(name='Current teachers', predicate=is_current_teacher)
    BOARD_MEMBERS = GroupDefinition(name='Board members', predicate=is_board_member)
    NEWSLETTER = GroupDefinition(name='Newsletter', predicate=newsletter)
    GET_INVOLVED = GroupDefinition(name='Want to get involved', predicate=get_involved)

    TEST = GroupDefinition(name='Test')

    DEFINITIONS = [
        ALL_TEACHERS,
        CURRENT_TEACHERS,
        BOARD_MEMBERS,
        NEWSLETTER,
        GET_INVOLVED,
        TEST,
    ]