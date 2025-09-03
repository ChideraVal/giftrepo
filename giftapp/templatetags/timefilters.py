from django import template

register = template.Library()

@register.filter
def format_seconds(value):
    try:
        value = value
        hours, remainder = divmod(value, 3600)
        minutes, seconds = divmod(remainder, 60)

        if hours:
            return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
        elif minutes:
            return f"{int(minutes)}m {int(seconds)}s"
        else:
            return f"{seconds}s"
    except (TypeError, ValueError):
        return "N/A"
