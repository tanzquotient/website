class GroupDefinition:

    def __init__(self, name, predicate):
        self.name = name
        self.predicate = predicate

    def matches(self, user):
        return self.predicate(user)