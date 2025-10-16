from django.db.models.signals import post_save, post_delete, post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.core.cache import cache
from django.template.loader import render_to_string
from django.conf import settings
from .models import Post, Category
from django.urls import reverse
from .utils import clear_post_cache

@receiver(post_save, sender=User)
def add_user_to_common_group(sender, instance, created, **kwargs):
    if created:
        try:
            common_group = Group.objects.get(name='common')
            instance.groups.add(common_group)
            print(f"Пользователь {instance.email} добавлен в группу common")  # Для отладки
        except Group.DoesNotExist:
            print("Группа 'common' не найдена! Создайте ее в админке.")


def send_welcome_email(sender, instance, created, **kwargs):
    if created:  # Отправляем только для новых пользователей
        # Формируем контекст для письма
        context = {
            'username': instance.username,
            'activation_url': f"http://127.0.0.1:8000{reverse('account_login')}",
            'site_url': 'http://127.0.0.1:8000',
        }

        # HTML версия письма
        html_message = render_to_string('account/email/welcome_email.html', context)

        # Текстовая версия письма
        text_message = render_to_string('account/email/welcome_email.txt', context)

        # Отправляем письмо
        send_mail(
            subject=f'Добро пожаловать в News Portal, {instance.username}! 🎉',
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.email],
            html_message=html_message,
            fail_silently=False,
        )


@receiver(post_save, sender=Post)
def notify_subscribers(sender, instance, created, **kwargs):
    if created and instance.post_type == 'AR':  # Только для статей
        categories = instance.categories.all()

        for category in categories:
            subscribers = category.subscribers.all()

            for subscriber in subscribers:
                context = {
                    'post': instance,
                    'user': subscriber,
                    'category': category,
                    'post_url': f"http://127.0.0.1:8000/news/{instance.id}/",
                }

                html_content = render_to_string('news/email/new_post_notification.html', context)
                text_content = render_to_string('news/email/new_post_notification.txt', context)

                # РЕАЛЬНАЯ ОТПРАВКА
                send_mail(
                    subject=instance.title,
                    message=text_content,
                    from_email='noreply@newsportal.com',
                    recipient_list=[subscriber.email],
                    html_message=html_content,
                    fail_silently=False,
                )


@receiver(post_save, sender=Post)
@receiver(post_delete, sender=Post)
def clear_cache_on_post_change(sender, instance, **kwargs):
    clear_post_cache(sender, instance, **kwargs)

@receiver(post_save, sender=Category)
@receiver(post_delete, sender=Category)
def clear_category_cache(sender, instance, **kwargs):
    # Очищаем кэш категорий
    cache.delete('categories')


@receiver(post_save, sender=Post)
@receiver(post_delete, sender=Post)
def clear_post_cache(sender, instance, **kwargs):
    """Очистка кэша при изменении постов"""
    try:
        # Очищаем кэш детальной страницы
        if instance.post_type == 'NW':
            cache.delete(f'news_detail_{instance.id}')
        elif instance.post_type == 'AR':
            cache.delete(f'article_detail_{instance.id}')

        # Очищаем основные кэши списков
        cache_keys_to_clear = [
            'news_list',
            'article_list',
            'articles_header',
            'articles_pagination_1',
            'articles_pagination_2',
            'news_header',
            'news_pagination_1',
            'news_pagination_2',
            'navigation',
            'footer'
        ]

        for key in cache_keys_to_clear:
            cache.delete(key)

        # Очищаем кэш связанных статей (правильно работаем с categories)
        if hasattr(instance, 'categories'):
            categories = instance.categories.all()
            for category in categories:
                cache.delete(f'related_articles_{category.id}')

        print(f"Кэш очищен для поста {instance.id}")

    except Exception as e:
        print(f"Ошибка при очистке кэша: {e}")

@receiver(post_migrate)
def create_authors_group(sender, **kwargs):
    if sender.name == 'news':
        group, created = Group.objects.get_or_create(name='authors')
        if created:
            # Добавляем разрешения для постов
            content_type = ContentType.objects.get_for_model(Post)
            permissions = Permission.objects.filter(content_type=content_type)
            group.permissions.set(permissions)
            print("Группа 'authors' создана с разрешениями")