import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newsportal.settings')
django.setup()

from django.core.management import call_command
from news.models import Post, Category


def restore_fixed():
    print("=== ВОССТАНОВЛЕНИЕ ДАННЫХ (ИСПРАВЛЕННАЯ ВЕРСИЯ) ===")

    # Проверяем текущее состояние
    articles_before = Post.objects.filter(post_type='AR').count()
    categories_before = Category.objects.all().count()

    print(f"📊 Перед восстановлением:")
    print(f"   Статей: {articles_before}")
    print(f"   Категорий: {categories_before}")

    # Ищем ВСЕ JSON файлы
    json_files = [f for f in os.listdir('.') if f.endswith('.json')]

    if not json_files:
        print("❌ JSON файлы не найдены!")
        return

    print("\n📂 Все найденные JSON файлы:")
    for i, file in enumerate(json_files, 1):
        print(f"   {i}. {file}")

    # Определяем какие файлы что содержат
    articles_files = []
    categories_files = []
    other_files = []

    for file in json_files:
        if 'article' in file.lower():
            articles_files.append(file)
        elif 'categor' in file.lower():  # category, categories
            categories_files.append(file)
        else:
            other_files.append(file)

    print(f"\n📄 Файлы со статьями: {articles_files}")
    print(f"📁 Файлы с категориями: {categories_files}")
    print(f"📦 Прочие файлы: {other_files}")

    # Восстанавливаем в правильном порядке: сначала категории, потом статьи
    files_to_restore = categories_files + articles_files + other_files

    print(f"\n🔄 Порядок восстановления: {files_to_restore}")

    for backup_file in files_to_restore:
        print(f"\n🔄 Восстановление из {backup_file}...")
        try:
            call_command('loaddata', backup_file)
            print(f"✅ {backup_file} - успешно восстановлен!")
        except Exception as e:
            print(f"❌ Ошибка при восстановлении {backup_file}: {e}")

    # Проверяем результат
    articles_after = Post.objects.filter(post_type='AR').count()
    categories_after = Category.objects.all().count()

    print(f"\n📊 После восстановления:")
    print(f"   Статей: {articles_after} (добавлено: {articles_after - articles_before})")
    print(f"   Категорий: {categories_after} (добавлено: {categories_after - categories_before})")


if __name__ == '__main__':
    restore_fixed()