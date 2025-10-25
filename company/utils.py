import markdown
import bleach
from django.utils.safestring import mark_safe

def markdownify(text):
    if not text:
        return ""
    html = markdown.markdown(text, extensions=["fenced_code", "codehilite"])
    allowed_tags = [
        'p', 'strong', 'em', 'ul', 'ol', 'li',
        'a', 'h1', 'h2', 'h3', 'blockquote', 'code', 'pre', 'br'
    ]
    clean_html = bleach.clean(html, tags=allowed_tags, strip=True)
    return mark_safe(clean_html)