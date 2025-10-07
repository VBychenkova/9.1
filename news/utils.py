from django.utils import timezone
from .models import Post
from django.core.cache import cache

def get_user_post_limit_info(user):
    """
    Возвращает информацию о лимите публикаций пользователя
    """
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

    today_posts_count = Post.objects.filter(
        author__user=user,
        created_at__gte=today_start
    ).count()

    return {
        'today_posts_count': today_posts_count,
        'limit': 3,
        'remaining_posts': 3 - today_posts_count,
        'can_publish': today_posts_count < 3
    }


def clear_post_cache(sender, instance, **kwargs):
    """Очистка кэша при изменении поста"""
    # Очищаем кэш детальной страницы поста
    cache.delete(f'post_detail_{instance.id}')
    # Очищаем кэш списков
    cache.delete('post_list')
    cache.delete('news_list')
    cache.delete('articles_list')

def get_cached_popular_posts():
    """Кэширование популярных постов"""
    popular_posts = cache.get('popular_posts')
    if not popular_posts:
        from .models import Post
        popular_posts = Post.objects.filter(
            rating__gt=100
        ).order_by('-rating')[:5]
        cache.set('popular_posts', popular_posts, 180)  # 2 минуты
    return popular_posts