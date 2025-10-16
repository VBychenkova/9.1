import django_filters
from django import forms
from .models import Post, Category


class PostFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Поиск по заголовку'
    )

    categories = django_filters.ModelMultipleChoiceFilter(
        queryset=Category.objects.all(),
        widget=django_filters.widgets.CSVWidget,
        label='Категории'
    )

    created_after = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='gte',
        label='Создано после',
        widget=django_filters.widgets.DateRangeWidget
    )

    created_before = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='lte',
        label='Создано до'
    )

    rating_min = django_filters.NumberFilter(
        field_name='rating',
        lookup_expr='gte',
        label='Рейтинг от'
    )

    rating_max = django_filters.NumberFilter(
        field_name='rating',
        lookup_expr='lte',
        label='Рейтинг до'
    )

    only_popular = django_filters.BooleanFilter(
        field_name='rating',
        lookup_expr='gte',
        label='Только популярные',
        method='filter_popular'
    )

    only_recent = django_filters.BooleanFilter(
        label='Только свежие',
        method='filter_recent'
    )

    class Meta:
        model = Post
        fields = ['post_type', 'categories', 'author']

    def filter_popular(self, queryset, name, value):
        if value:
            return queryset.filter(rating__gte=100)
        return queryset

    def filter_recent(self, queryset, name, value):
        if value:
            from django.utils import timezone
            from datetime import timedelta
            week_ago = timezone.now() - timedelta(days=7)
            return queryset.filter(created_at__gte=week_ago)
        return queryset


class NewsFilter(PostFilter):
    title = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Поиск по заголовку'
    )

    categories = django_filters.ModelMultipleChoiceFilter(
        queryset=Category.objects.all(),
        label='Категории'
    )

    class Meta:
        model = Post
        fields = ['categories', 'author']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = self.queryset.filter(post_type='NW')


class ArticleFilter(PostFilter):
    class Meta:
        model = Post
        fields = ['categories', 'author']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = self.queryset.filter(post_type='AR')