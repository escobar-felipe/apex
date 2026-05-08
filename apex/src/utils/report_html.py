from bs4 import BeautifulSoup


BLOCKED_TAGS = {"script", "iframe", "object", "embed", "form", "input", "button", "meta", "link", "base"}
BLOCKED_ATTR_PREFIXES = ("on",)
BLOCKED_ATTRS = {"srcdoc"}


def sanitize_report_html(html):
    soup = BeautifulSoup(html or "", "html.parser")

    for tag in soup.find_all(BLOCKED_TAGS):
        tag.decompose()

    for tag in soup.find_all(True):
        for attr in list(tag.attrs):
            attr_lower = attr.lower()
            value = tag.attrs.get(attr)
            value_text = " ".join(value) if isinstance(value, list) else str(value)
            if (
                attr_lower in BLOCKED_ATTRS
                or attr_lower.startswith(BLOCKED_ATTR_PREFIXES)
                or value_text.strip().lower().startswith("javascript:")
            ):
                del tag.attrs[attr]

    return str(soup)
