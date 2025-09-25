import os
import django
import subprocess

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newsportal.settings')
django.setup()

from news.models import Comment, Post, Category, Author

print("=== ОЧИСТКА БАЗЫ ДАННЫХ ===")
Comment.objects.all().delete()
Post.objects.all().delete()
Category.objects.all().delete()
Author.objects.all().delete()
print("Данные удалены")

print("\n=== ЗАПУСК ОСНОВНОГО СКРИПТА ===")
# Запускаем script.py через shell
result = subprocess.run(['python', 'manage.py', 'shell', '<', 'script.py'],
                       capture_output=True, text=True, shell=True)
print(result.stdout)
if result.stderr:
    print("Ошибки:", result.stderr)

print("=== ВЫПОЛНЕНИЕ ЗАВЕРШЕНО ===")