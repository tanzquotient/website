from tq_website import settings


class TranslationUtils:

    @staticmethod
    def get_text_with_language_fallback(model, attribute):
        for lang in [model.get_current_language()] + settings.PARLER_LANGUAGES['default']['fallbacks']:
            val = model.safe_translation_getter(attribute, language_code=lang)
            if val:
                return val
        return None
