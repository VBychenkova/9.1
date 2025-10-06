from django.utils import timezone
from .models import Post


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