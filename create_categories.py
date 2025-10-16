import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newsportal.settings')
django.setup()

from news.models import Category
from django.utils.translation import gettext as _


def create_categories():
    categories_data = [
        # Русское название, Английское название
        ('Политика', 'Politics'),
        ('Экономика', 'Economy'),
        ('Технологии', 'Technology'),
        ('Спорт', 'Sports'),
        ('Культура', 'Culture'),
        ('Наука', 'Science'),
        ('Здоровье', 'Health'),
        ('Происшествия', 'Incidents'),
        ('Общество', 'Society'),
        ('Международные', 'International'),
    ]

    created_count = 0
    for ru_name, en_name in categories_data:
        category, created = Category.objects.get_or_create(name=ru_name)
        if created:
            created_count += 1
            print(f"✅ Создана категория: {ru_name} / {en_name}")
        else:
            print(f"ℹ️ Категория уже существует: {ru_name}")

    print(f"\nВсего создано категорий: {created_count}")
    print(f"Всего категорий в базе: {Category.objects.count()}")


if __name__ == '__main__':
    create_categories()