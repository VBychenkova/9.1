import os
import django
import sys

sys.path.append('C:/Users/timka/PycharmProjects/9.1')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newsportal.settings')
django.setup()

from django.contrib.auth.models import User
from news.models import Author, Category, Post, PostCategory, Comment

print("=== Создание/получение данных ===")

# 1. Пользователи - создаем если не существуют
user1, created = User.objects.get_or_create(
    username='user1',
    defaults={'password': 'test123'}
)
if created:
    user1.set_password('test123')
    user1.save()
    print("Создан user1")
else:
    print("user1 уже существует")

user2, created = User.objects.get_or_create(
    username='user2',
    defaults={'password': 'test123'}
)
if created:
    user2.set_password('test123')
    user2.save()
    print("Создан user2")
else:
    print("user2 уже существует")

# 2. Авторы - удаляем старых и создаем новых
Author.objects.filter(user__in=[user1, user2]).delete()
author1 = Author.objects.create(user=user1)
author2 = Author.objects.create(user=user2)
print("Авторы созданы")

# 3. Категории - очищаем и создаем заново
Category.objects.all().delete()
cat1 = Category.objects.create(name='Спорт')
cat2 = Category.objects.create(name='Политика')
cat3 = Category.objects.create(name='Образование')
cat4 = Category.objects.create(name='Технологии')
print("Категории созданы")

# 4. Посты и комментарии - очищаем и создаем заново
Post.objects.all().delete()
Comment.objects.all().delete()

# ... остальной код создания постов и комментариев