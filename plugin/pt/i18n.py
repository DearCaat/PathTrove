"""Language of a call: `zh` or `en`. Default from the environment variable PATHTROVE_LANG, else zh."""
from __future__ import annotations

import os

from .errors import PtError

LANGS = ("zh", "en")


def norm_lang(lang: str | None) -> str:
    """An explicit lang must be zh or en; None takes PATHTROVE_LANG (zh-CN, en_US, ... accepted), then zh."""
    if lang not in (None, ""):
        v = str(lang).strip().lower().replace("_", "-")
        if v[:2] in LANGS and v in (v[:2], f"{v[:2]}-cn", f"{v[:2]}-us", f"{v[:2]}-gb", f"{v[:2]}-tw"):
            return v[:2]
        raise PtError(f"lang must be zh or en, got {lang!r} / lang 只能是 zh 或 en，收到 {lang!r}")
    env = os.environ.get("PATHTROVE_LANG", "").strip().lower().replace("_", "-")
    return env[:2] if env[:2] in LANGS else "zh"


def L(lang: str, en: str, zh: str) -> str:
    """The text of the call's language."""
    return zh if lang == "zh" else en
