import bleach
from django.conf import settings


def sanitize_html(html: str) -> str:
    if not html:
        return ''
    return bleach.clean(
        html,
        tags=settings.BLEACH_ALLOWED_TAGS,
        attributes=settings.BLEACH_ALLOWED_ATTRIBUTES,
        strip=True,
    )
