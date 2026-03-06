import re
import html


def safe_key(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_]+", "_", value)


def escape_html(value: str) -> str:
    return html.escape(value or "")