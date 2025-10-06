from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta
from .models import Subscription, Post, Category


@shared_task
def send_weekly_digest():
    """Отправляет еженедельную рассылку подписчикам"""
    try:
        # Дата неделю назад
        week_ago = timezone.now() - timedelta(days=7)

        print("Starting weekly digest...")

        # Для каждой категории
        for category in Category.objects.all():
            # Новые статьи в категории за неделю
            new_posts = Post.objects.filter(
                categories=category,
                created_at__gte=week_ago,
                post_type='AR'  # Только статьи
            )

            if new_posts.exists():
                # Получаем подписчиков категории
                subscribers = category.subscribers.all()

                print(f"Category {category.name}: {new_posts.count()} new posts, {subscribers.count()} subscribers")

                for subscriber in subscribers:
                    # Формируем контент письма
                    context = {
                        'user': subscriber,
                        'category': category,
                        'posts': new_posts,
                        'week_start': week_ago.date(),
                        'week_end': timezone.now().date(),
                    }

                    html_message = render_to_string('news/email/weekly_digest.html', context)
                    text_message = render_to_string('news/email/weekly_digest.txt', context)

                    # РЕАЛЬНАЯ ОТПРАВКА EMAIL
                    send_mail(
                        subject=f'Еженедельная рассылка: новые статьи в категории "{category.name}"',
                        message=text_message,
                        from_email='noreply@newsportal.com',
                        recipient_list=[subscriber.email],
                        html_message=html_message,
                        fail_silently=False,
                    )

                    print(f"✅ Email sent to {subscriber.email} with {new_posts.count()} posts")

        print("Weekly digest completed successfully")
        return f"Weekly digest sent for {Category.objects.count()} categories"

    except Exception as e:
        print(f"Error in weekly digest: {e}")
        return f"Error: {e}"