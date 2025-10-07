from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
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


receiver(post_save, sender=Post)


@receiver(post_delete, sender=Post)
def clear_article_cache(sender, instance, **kwargs):
    """Очистка кэша при изменении статей"""
    if instance.post_type == 'AR':  # Только для статей
        # Очищаем кэш детальной страницы статьи
        cache.delete(f'article_detail_{instance.id}')

        # Очищаем кэш списка статей
        cache.delete_pattern('*article_list*')

        # Очищаем кэш связанных статей
        cache.delete(f'related_articles_{instance.category.id}')

        print(f"Кэш для статьи {instance.id} очищен")