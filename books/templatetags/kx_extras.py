from django import template

register = template.Library()


@register.filter
def yulduz_pct(value):
    """Bahoni (0-5) yulduzlar kengligi uchun foizga aylantiradi."""
    try:
        return round(float(value) / 5 * 100, 1)
    except (TypeError, ValueError):
        return 0
