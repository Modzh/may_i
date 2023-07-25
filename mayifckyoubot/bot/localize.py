import enum
import typing as ty


class Language(enum.Enum):
    EN = "en"
    RU = "ru"


def translate(tag: str, language: Language, raise_exception: bool = False) -> str:
    from bot.models import Document

    default = tag

    document = Document.objects.filter(tag=tag, language=language).first()
    if document is None and raise_exception:
        raise KeyError(f"Translation key '{tag}' not found")
    if document is None:
        return default
    return ty.cast(str, document.text if document.text is not None else default)
