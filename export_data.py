import os
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newsportal.settings')
django.setup()

from news.models import Post, Category
from django.core import serializers


def export_simple():
    print("=== ПРОСТОЙ ЭКСПОРТ ДАННЫХ ===")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 1. Экспорт статей
    articles = Post.objects.filter(post_type='AR')
    articles_json = serializers.serialize('json', articles, indent=2, use_natural_foreign_keys=True)

    articles_filename = f'articles_{timestamp}.json'
    with open(articles_filename, 'w', encoding='utf-8') as f:
        f.write(articles_json)

    # 2. Экспорт категорий
    categories = Category.objects.all()
    categories_json = serializers.serialize('json', categories, indent=2)

    categories_filename = f'categories_{timestamp}.json'
    with open(categories_filename, 'w', encoding='utf-8') as f:
        f.write(categories_json)

    print(f"✅ Статей экспортировано: {articles.count()}")
    print(f"✅ Категорий экспортировано: {categories.count()}")
    print(f"📁 Файлы: {articles_filename}, {categories_filename}")

    # Показываем информацию о статьях
    for article in articles[:3]:  # Первые 3 статьи
        cats = list(article.categories.all().values_list('name', flat=True))
        print(f"   - {article.title} | Категории: {cats}")


if __name__ == '__main__':
    export_simple()