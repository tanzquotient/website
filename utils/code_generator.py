import shortuuid


class CodeGenerator:
    # Avoid similar looking characters:
    # 0 O
    # 1 I l
    # 2 Z
    # 5 S
    non_ambiguous_alphabet_for_humans = "ABCDEFGHJKMNPQRTUVWXY346789"

    @staticmethod
    def short_uuid() -> str:
        instance = shortuuid.ShortUUID()
        return instance.uuid()

    @staticmethod
    def short_uuid_without_ambiguous_characters(length: int = 6) -> str:
        instance = shortuuid.ShortUUID(
            alphabet=CodeGenerator.non_ambiguous_alphabet_for_humans
        )
        return instance.random(length=length)
