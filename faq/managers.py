from parler.managers import TranslatableManager


class QuestionManager(TranslatableManager):
    def displayed(self):
        return self.all().filter(display=True).order_by("position")
