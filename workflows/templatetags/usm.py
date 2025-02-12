from django import template
from django.utils.html import escape, format_html, mark_safe

register = template.Library()

links = {
    "$document$": "https://usmwiki.com/index.php/Document",
    "$document$": "https://usmwiki.com/index.php/Document",
    "$party$": "https://usmwiki.com/index.php/Party",
    "$Party$": "https://usmwiki.com/index.php/Party",
    "$profile$": "https://usmwiki.com/index.php/Profile",
    "$Profile$": "https://usmwiki.com/index.php/Profile",
    "$risk$": "https://usmwiki.com/index.php/Risk",
    "$Risk$": "https://usmwiki.com/index.php/Risk",
    "$task$": "https://usmwiki.com/index.php/Task",
    "$Task$": "https://usmwiki.com/index.php/Task",
    "$employee$": "https://usmwiki.com/index.php/Employee",
    "$Employee$": "https://usmwiki.com/index.php/Employee",
    "$profile$": "https://usmwiki.com/index.php/Profile",
    "$Profile$": "https://usmwiki.com/index.php/Profile",
    "$workflow$": "https://usmwiki.com/index.php/workflow",
    "$Workflow$": "https://usmwiki.com/index.php/Workflow",
    "$Requester$": "https://usmwiki.com/index.php/Requester",
    "$requester$": "https://usmwiki.com/index.php/Requester",
    "$responsibility$": "https://usmwiki.com/index.php/Responsibility",
    "$Responsibility$": "https://usmwiki.com/index.php/Responsibility",
}

@register.filter
def usm_format_links(text):
    text = escape(text)

    for link, url in links.items():
        display_text = link.replace('$', '')
        text = text.replace(link, format_html('<a class="text-white" href="{}">{}</a>', url, display_text))
    return mark_safe(text)
