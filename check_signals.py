import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newsportal.settings')
django.setup()

from news.models import Post


def check_signal_connection():
    from django.db.models.signals import post_delete
    from news import signals

    # Проверяем подключен ли сигнал
    receivers = post_delete._live_receivers(Post)
    print(f"📡 Подключено receivers для post_delete: {len(receivers)}")

    for receiver in receivers:
        print(f"   - {receiver}")

    # Проверяем структуру модели Post
    print("\n🔍 Структура модели Post:")
    for field in Post._meta.get_fields():
        print(f"   - {field.name} ({field.get_internal_type()})")

    # Проверяем существование поля categories
    if hasattr(Post, 'categories'):
        print("✅ Поле 'categories' существует")
        # Проверим на реальном объекте
        post = Post.objects.first()
        if post:
            print(f"✅ categories.all() работает: {list(post.categories.all().values_list('name', flat=True))}")
        else:
            print("⚠️ Нет постов для проверки")
    else:
        print("❌ Поле 'categories' не существует")


if __name__ == '__main__':
    check_signal_connection()