class GroupDefinition:

    def __init__(self, name, predicate=None, is_manual=False):
        self.name = name
        self.predicate = predicate
        self.is_manual = is_manual

    def matches(self, user):
        return self.predicate(user)

    def is_manual(self):
        return self.predicate is None