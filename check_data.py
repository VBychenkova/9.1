import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newsportal.settings')
django.setup()

from news.models import Post, Category


def check_data():
    print("=== ТЕКУЩИЕ ДАННЫЕ ===")

    # Статьи
    articles = Post.objects.filter(post_type='AR')
    print(f"📄 Статей в базе: {articles.count()}")
    for article in articles[:5]:
        cats = list(article.categories.all().values_list('name', flat=True))
        print(f"   - {article.title} (ID: {article.id})")
        print(f"     Категории: {cats}")

    # Категории
    categories = Category.objects.all()
    print(f"📁 Категорий в базе: {categories.count()}")
    for category in categories:
        print(f"   - {category.name} (ID: {category.id})")

    return articles.count(), categories.count()


if __name__ == '__main__':
    check_data()