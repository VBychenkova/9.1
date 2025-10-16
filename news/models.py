from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_('User'))
    rating = models.IntegerField(default=0, verbose_name=_('Rating'))

    def update_rating(self):
        """Обновляет рейтинг автора"""
        # Суммарный рейтинг статей автора × 3
        post_rating = self.post_set.aggregate(pr=Sum('rating'))['pr'] or 0
        post_rating *= 3

        # Суммарный рейтинг комментариев автора
        comment_rating = self.user.comment_set.aggregate(cr=Sum('rating'))['cr'] or 0

        # Суммарный рейтинг комментариев к статьям автора
        from .models import Comment  # Локальный импорт для избежания циклических зависимостей
        post_comment_rating = Comment.objects.filter(post__author=self).aggregate(pcr=Sum('rating'))['pcr'] or 0

        self.rating = post_rating + comment_rating + post_comment_rating
        self.save()

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = _('Author')
        verbose_name_plural = _('Authors')


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_('Name'))
    subscribers = models.ManyToManyField(
        User,
        through='Subscription',
        related_name='subscribed_categories',
        blank=True,
        verbose_name=_('Subscribers')
    )

    @property
    def post_count(self):
        """Количество постов в категории"""
        return self.post_set.count()

    @property
    def news_count(self):
        """Количество новостей в категории"""
        return self.post_set.filter(post_type='NW').count()

    @property
    def articles_count(self):
        """Количество статей в категории"""
        return self.post_set.filter(post_type='AR').count()

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    def __str__(self):
        return self.name


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('User'))
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name=_('Category'))
    subscribed_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Subscribed at'))

    class Meta:
        unique_together = ('user', 'category')
        verbose_name = _('Subscription')
        verbose_name_plural = _('Subscriptions')

    def __str__(self):
        return f"{self.user.username} - {self.category.name}"


class Post(models.Model):
    ARTICLE = 'AR'
    NEWS = 'NW'
    POST_TYPES = [
        (ARTICLE, _('Article')),
        (NEWS, _('News')),
    ]

    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        verbose_name=_('Author')
    )
    post_type = models.CharField(
        max_length=2,
        choices=POST_TYPES,
        verbose_name=_('Post type')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated at')
    )
    categories = models.ManyToManyField(
        Category,
        through='PostCategory',
        verbose_name=_('Categories'),
        blank=True  # Добавляем blank=True
    )
    title = models.CharField(
        max_length=200,
        verbose_name=_('Title')
    )
    content = models.TextField(verbose_name=_('Content'))
    rating = models.IntegerField(
        default=0,
        verbose_name=_('Rating')
    )
    is_published = models.BooleanField(
        default=True,
        verbose_name=_('Is published')
    )

    def like(self):
        """Увеличивает рейтинг на 1"""
        self.rating += 1
        self.save()

    def dislike(self):
        """Уменьшает рейтинг на 1"""
        self.rating -= 1
        self.save()

    def preview(self):
        """Возвращает превью контента"""
        return self.content[:124] + '...' if len(self.content) > 124 else self.content

    #def save(self, *args, **kwargs):
    #    """При сохранении обновляет updated_at"""
    #    # Упрощаем метод save - убираем сложную логику
    #    if self.pk:
    #        self.updated_at = timezone.now()
    #    super().save(*args, **kwargs)

    @property
    def short_title(self):
        """Сокращенный заголовок"""
        if len(self.title) > 50:
            return self.title[:50] + '...'
        return self.title

    @property
    def is_recent(self):
        """Является ли пост свежим (менее 7 дней)"""
        return (timezone.now() - self.created_at).days < 7

    def get_absolute_url(self):
        """Возвращает абсолютный URL для детальной страницы"""
        if self.post_type == 'NW':
            return reverse('news_detail', kwargs={'pk': self.pk})
        else:
            return reverse('article_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return f"{self.title} ({self.get_post_type_display()})"

    class Meta:
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')
        ordering = ['-created_at']


class PostCategory(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name=_('Post')
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name=_('Category')
    )

    class Meta:
        verbose_name = _('Post Category')
        verbose_name_plural = _('Post Categories')

    def __str__(self):
        return f"{self.post.title} - {self.category.name}"


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name=_('Post')
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('User')
    )
    text = models.TextField(verbose_name=_('Text'))
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at')
    )
    rating = models.IntegerField(
        default=0,
        verbose_name=_('Rating')
    )
    is_published = models.BooleanField(
        default=True,
        verbose_name=_('Is published')
    )

    def like(self):
        """Увеличивает рейтинг комментария на 1"""
        self.rating += 1
        self.save()

    def dislike(self):
        """Уменьшает рейтинг комментария на 1"""
        self.rating -= 1
        self.save()

    @property
    def short_text(self):
        """Сокращенный текст комментария"""
        if len(self.text) > 100:
            return self.text[:100] + '...'
        return self.text

    def __str__(self):
        return f"{_('Comment by')} {self.user.username} {_('on')} {self.post.title}"

    class Meta:
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['post']),
            models.Index(fields=['user']),
        ]


# Дополнительные модели для расширенной функциональности
class Article(models.Model):
    """Расширенная модель для статей (если нужна отдельно от Post)"""
    title = models.CharField(
        _('Title'),
        max_length=200
    )
    content = models.TextField(_('Content'))
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name=_('Category'),
        null=True,  # Разрешить null для существующих записей
        blank=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Author'),
        null=True,  # Разрешить null для существующих записей
        blank=True
    )
    created_at = models.DateTimeField(
        _('Created at'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('Updated at'),
        auto_now=True
    )
    is_published = models.BooleanField(
        _('Is published'),
        default=True
    )

    class Meta:
        verbose_name = _('Article')
        verbose_name_plural = _('Articles')
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('article_detail', kwargs={'pk': self.pk})


class News(models.Model):
    """Расширенная модель для новостей (если нужна отдельно от Post)"""
    title = models.CharField(
        _('Title'),
        max_length=200
    )
    content = models.TextField(_('Content'))
    categories = models.ManyToManyField(
        Category,
        verbose_name=_('Categories'),
        blank=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Author'),
        null=True,  # Разрешить null для существующих записей
        blank=True
    )
    created_at = models.DateTimeField(
        _('Created at'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('Updated at'),
        auto_now=True
    )
    is_published = models.BooleanField(
        _('Is published'),
        default=True
    )

    class Meta:
        verbose_name = _('News')
        verbose_name_plural = _('News')
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('news_detail', kwargs={'pk': self.pk})


# Модель для хранения пользовательских настроек (часовой пояс и т.д.)
class UserProfile(models.Model):
    """Профиль пользователя для дополнительных настроек"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('User')
    )
    timezone = models.CharField(
        _('Timezone'),
        max_length=50,
        default='UTC',
        blank=True
    )
    language = models.CharField(
        _('Language'),
        max_length=10,
        default='ru',
        blank=True
    )
    theme = models.CharField(
        _('Theme'),
        max_length=10,
        choices=[
            ('light', _('Light')),
            ('dark', _('Dark')),
            ('auto', _('Auto')),
        ],
        default='auto'
    )
    email_notifications = models.BooleanField(
        _('Email notifications'),
        default=True
    )

    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')

    def __str__(self):
        return f"{self.user.username} {_('Profile')}"