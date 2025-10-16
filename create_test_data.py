import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newsportal.settings')
django.setup()

from django.contrib.auth.models import User
from news.models import Author, Category, Post


def create_test_data():
    # Создаем пользователя
    user, created = User.objects.get_or_create(
        username='test_author',
        defaults={
            'email': 'test@example.com',
            'is_staff': False,
            'is_superuser': False
        }
    )
    if created:
        user.set_password('testpassword123')
        user.save()
        print("Создан пользователь: test_author")

    # Создаем автора
    author, created = Author.objects.get_or_create(user=user)
    if created:
        print("Создан автор")

    # Создаем категорию
    category, created = Category.objects.get_or_create(name='General')
    if created:
        print("Создана категория: General")

    # Создаем тестовую новость
    try:
        news = Post.objects.create(
            author=author,
            post_type='NW',
            title='Добро пожаловать в наш новостной портал!',
            content='Это тестовая новость для демонстрации работы сайта. Здесь будет отображаться актуальная информация и последние события.',
            rating=5,
            is_published=True
        )
        # Добавляем категорию через промежуточную модель
        from news.models import PostCategory
        PostCategory.objects.create(post=news, category=category)

        print("Успешно создана тестовая новость!")
        print(f"Заголовок: {news.title}")
        print(f"Автор: {news.author.user.username}")
        print(f"Тип: {news.get_post_type_display()}")

    except Exception as e:
        print(f"Ошибка при создании новости: {e}")
        print("Проверьте структуру базы данных и миграции")


if __name__ == '__main__':
    create_test_data()