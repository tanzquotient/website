class GroupDefinition:

    def __init__(self, name: str, predicate=None) -> None:
        self.name: str = name
        self.predicate = predicate

    def matches(self, user) -> bool:
        return self.predicate(user)

    def is_manual(self) -> bool:
        return self.predicate is None
