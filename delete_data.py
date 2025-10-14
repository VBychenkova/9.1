import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newsportal.settings')
django.setup()

from news.models import Post, Category
from django.core.cache import cache


def delete_fixed():
    print("=== УДАЛЕНИЕ ДАННЫХ С ИСПРАВЛЕННЫМИ СИГНАЛАМИ ===")

    # Подсчет перед удалением
    articles_count = Post.objects.filter(post_type='AR').count()
    categories_count = Category.objects.all().count()

    print(f"📄 Статей для удаления: {articles_count}")
    print(f"📁 Категорий для удаления: {categories_count}")

    if articles_count == 0 and categories_count == 0:
        print("❌ Нет данных для удаления")
        return

    # Подтверждение
    confirm = input("❓ Вы уверены, что хотите удалить эти данные? (y/n): ")

    if confirm.lower() == 'y':
        try:
            # Очищаем кэш вручную
            print("🧹 Очистка кэша...")
            cache.clear()

            # Удаляем данные - теперь сигналы должны работать правильно
            print("🗑️ Удаление статей...")
            deleted_articles = Post.objects.filter(post_type='AR').count()
            Post.objects.filter(post_type='AR').delete()
            print(f"✅ Удалено статей: {deleted_articles}")

            print("🗑️ Удаление категорий...")
            deleted_categories = Category.objects.all().count()
            Category.objects.all().delete()
            print(f"✅ Удалено категорий: {deleted_categories}")

            # Проверяем результат
            remaining_articles = Post.objects.filter(post_type='AR').count()
            remaining_categories = Category.objects.all().count()

            print(f"📊 Осталось статей: {remaining_articles}")
            print(f"📊 Осталось категорий: {remaining_categories}")
            print("✅ Все данные удалены!")

        except Exception as e:
            print(f"❌ Ошибка при удалении: {e}")
            print("⚠️ Проверьте файл signals.py на наличие ошибок")

    else:
        print("❌ Удаление отменено")


if __name__ == '__main__':
    delete_fixed()