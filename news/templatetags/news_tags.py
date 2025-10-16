from django import template
from news.models import Category, Post
from django.utils import timezone
from datetime import timedelta

register = template.Library()


@register.inclusion_tag('news/includes/categories_sidebar.html')
def show_categories():
    categories = Category.objects.annotate(
        post_count=models.Count('post'),
        news_count=models.Count('post', filter=models.Q(post__post_type='NW')),
        article_count=models.Count('post', filter=models.Q(post__post_type='AR'))
    )
    return {'categories': categories}


@register.inclusion_tag('news/includes/recent_posts.html')
def show_recent_posts(count=5, post_type=None):
    queryset = Post.objects.all()
    if post_type:
        queryset = queryset.filter(post_type=post_type)

    recent_posts = queryset.order_by('-created_at')[:count]
    return {'posts': recent_posts}


@register.inclusion_tag('news/includes/popular_posts.html')
def show_popular_posts(count=5, post_type=None):
    queryset = Post.objects.all()
    if post_type:
        queryset = queryset.filter(post_type=post_type)

    popular_posts = queryset.order_by('-rating')[:count]
    return {'posts': popular_posts}


@register.simple_tag
def get_post_stats():
    """Статистика по постам"""
    total_posts = Post.objects.count()
    total_news = Post.objects.filter(post_type='NW').count()
    total_articles = Post.objects.filter(post_type='AR').count()

    week_ago = timezone.now() - timedelta(days=7)
    recent_posts = Post.objects.filter(created_at__gte=week_ago).count()

    return {
        'total_posts': total_posts,
        'total_news': total_news,
        'total_articles': total_articles,
        'recent_posts': recent_posts,
    }