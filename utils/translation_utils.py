from typing import Optional

from parler.utils.context import switch_language

from tq_website import settings


class TranslationUtils:
    @staticmethod
    def get_text_with_language_fallback(model, attribute: str) -> Optional[str]:
        if model is None:
            return None
        for lang in [model.get_current_language()] + settings.PARLER_LANGUAGES[
            "default"
        ]["fallbacks"]:
            with switch_language(model, lang):
                val = getattr(model, attribute)
            if val:
                return val
        return None

    @staticmethod
    def get_text_with_language_fallback_or_empty(model, attribute: str) -> str:
        return TranslationUtils.get_text_with_language_fallback(model, attribute) or ""

    @staticmethod
    def copy_translations(old, new) -> None:
        for t in old.translations.all():
            t.pk = None
            t.master = new
            t.save()
