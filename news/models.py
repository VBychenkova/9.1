from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.urls import reverse
from django.utils import timezone
#from news.models import Post, Category, Author, Subscription


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def update_rating(self):
        # Суммарный рейтинг статей автора × 3
        post_rating = self.post_set.aggregate(pr=Sum('rating'))['pr'] or 0
        post_rating *= 3

        # Суммарный рейтинг комментариев автора
        comment_rating = self.user.comment_set.aggregate(cr=Sum('rating'))['cr'] or 0

        # Суммарный рейтинг комментариев к статьям автора
        post_comment_rating = Comment.objects.filter(post__author=self).aggregate(pcr=Sum('rating'))['pcr'] or 0

        self.rating = post_rating + comment_rating + post_comment_rating
        self.save()

    def __str__(self):
        return self.user.username


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    subscribers = models.ManyToManyField(User, through='Subscription', related_name='subscribed_categories')

    def __str__(self):
        return self.name

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
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'category')

class Post(models.Model):
    ARTICLE = 'AR'
    NEWS = 'NW'
    POST_TYPES = [
        (ARTICLE, 'Статья'),
        (NEWS, 'Новость'),
    ]

    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    post_type = models.CharField(max_length=2, choices=[('NW', 'Новость'), ('AR', 'Статья')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    categories = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=200)
    content = models.TextField()
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return self.content[:124] + '...' if len(self.content) > 124 else self.content

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('news_detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        # При сохранении обновляем updated_at
        if self.pk:  # Если объект уже существует
            self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.get_post_type_display()})"

    def get_absolute_url(self):
        if self.post_type == 'NW':
            return reverse('news_detail', kwargs={'pk': self.pk})
        else:
            return reverse('article_detail', kwargs={'pk': self.pk})

    @property
    def short_title(self):
        """Сокращенный заголовок"""
        if len(self.title) > 50:
            return self.title[:50] + '...'
        return self.title

    @property
    def preview(self):
        """Превью контента"""
        if len(self.content) > 150:
            return self.content[:150] + '...'
        return self.content

    @property
    def is_recent(self):
        """Является ли пост свежим (менее 7 дней)"""
        return (timezone.now() - self.created_at).days < 7

    @property
    def is_popular(self):
        """Является ли пост популярным"""
        return self.rating > 100

    class Meta:
        verbose_name = 'Публикация'
        verbose_name_plural = 'Публикации'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['post_type']),
            models.Index(fields=['rating']),
        ]


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.title}"


from django.db import models

# Create your models here.
