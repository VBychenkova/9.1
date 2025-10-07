from django import template
from django.core.cache import cache
from news.models import Category

register = template.Library()

@register.simple_tag
def get_cached_categories():
    categories = cache.get('categories')
    if not categories:
        categories = Category.objects.all()
        cache.set('categories', categories, 3600)  # 1 час
    return categories