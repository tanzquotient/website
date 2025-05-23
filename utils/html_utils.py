import re


class HTMLUtils:
    @staticmethod
    def html_has_text(html: str) -> bool:
        if html is None:
            return False
        return bool(re.sub(r"<[^>]*>", "", html).strip())
