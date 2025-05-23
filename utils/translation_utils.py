from typing import Optional, Callable

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
    def is_field_translated_in_all_languages(
        object, attribute: str, transform: Callable = lambda x: bool(x)
    ):
        for language in settings.LANGUAGES:
            language_code = language[0]
            if not transform(
                object.safe_translation_getter(
                    attribute, language_code=language_code, any_language=False
                )
            ):
                return False
        return True

    @staticmethod
    def copy_translations(old, new) -> None:
        for t in old.translations.all():
            t.pk = None
            t.master = new
            t.save()
