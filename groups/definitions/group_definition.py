class GroupDefinition:

    def __init__(self, name, predicate=None):
        self.name = name
        self.predicate = predicate

    def matches(self, user):
        return self.predicate(user)

    def is_manual(self):
        return self.predicate is None