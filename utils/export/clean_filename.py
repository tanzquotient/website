import re


def clean_filename(name):
    replacements = {
        "ü": "ue",
        "Ü": "Ue",
        "ä": "ae",
        "Ä": "Ae",
        "ö": "oe",
        "Ö": "Oe",
        " ": "_",
    }
    for original, substitute in replacements.items():
        name = name.replace(original, substitute)

    invalid_chars = re.compile(r"[^\w\-_ .]", re.IGNORECASE | re.UNICODE)
    name = invalid_chars.sub("", name)

    return name
