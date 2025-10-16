from django.contrib import admin
from news.models import Post, Category, Author, Subscription


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'post_type', 'author', 'category_list', 'rating', 'created_at', 'is_recent']
    list_filter = ['post_type', 'created_at', 'rating', 'author']
    search_fields = ['title', 'content', 'author__user__username']
    readonly_fields = ['created_at', 'rating', 'updated_at', 'category_list_display']
    date_hierarchy = 'created_at'

    # Не включаем categories в fields - используем только для отображения
    fields = [
        'title',
        'content',
        'post_type',
        'author',
        'rating',
        'created_at',
        'updated_at',
        'category_list_display'  # Только для чтения
    ]

    def category_list(self, obj):
        """Отображение категорий в списке"""
        return ", ".join([cat.name for cat in obj.categories.all()])

    category_list.short_description = 'Категории'

    def category_list_display(self, obj):
        """Отображение категорий в форме редактирования"""
        categories = obj.categories.all()
        if categories:
            return ", ".join([f"{cat.name} (ID: {cat.id})" for cat in categories])
        return "Нет категорий"

    category_list_display.short_description = 'Категории (только просмотр)'

    def is_recent(self, obj):
        from django.utils import timezone
        return (timezone.now() - obj.created_at).days < 7

    is_recent.boolean = True
    is_recent.short_description = 'Свежая'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'post_count', 'news_count', 'articles_count', 'subscriber_count']
    search_fields = ['name', 'description']

    def post_count(self, obj):
        return obj.post_set.count()

    post_count.short_description = 'Всего постов'

    def news_count(self, obj):
        return obj.post_set.filter(post_type='NW').count()

    news_count.short_description = 'Новостей'

    def articles_count(self, obj):
        return obj.post_set.filter(post_type='AR').count()

    articles_count.short_description = 'Статей'

    def subscriber_count(self, obj):
        return obj.subscription_set.count()

    subscriber_count.short_description = 'Подписчики'


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['user', 'post_count', 'rating_avg']
    list_filter = ['user__date_joined']
    search_fields = ['user__username', 'user__email']

    def post_count(self, obj):
        return obj.post_set.count()

    post_count.short_description = 'Постов'

    def rating_avg(self, obj):
        from django.db.models import Avg
        result = obj.post_set.aggregate(Avg('rating'))
        return round(result['rating__avg'] or 0, 2)

    rating_avg.short_description = 'Ср. рейтинг'


admin.site.register(Subscription)