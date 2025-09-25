# -*- coding: utf-8 -*-
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newsportal.settings')
django.setup()

from django.contrib.auth.models import User
from news.models import Author, Category, Post, PostCategory, Comment

print("=== Начало выполнения ===")

# Удаляем старых пользователей если существуют
User.objects.filter(username__in=['user1', 'user2']).delete()

# 1. Создание пользователей
user1 = User.objects.create_user('user1', password='test123')
user2 = User.objects.create_user('user2', password='test123')
print("Пользователи созданы")

# 2. Создание авторов
author1 = Author.objects.create(user=user1)
author2 = Author.objects.create(user=user2)
print("Авторы созданы")

# 3. Добавление категорий
Category.objects.all().delete()  # Очищаем старые категории
cat1 = Category.objects.create(name='Спорт')
cat2 = Category.objects.create(name='Политика')
cat3 = Category.objects.create(name='Образование')
cat4 = Category.objects.create(name='Технологии')
print("Категории созданы")

# 4. Создание статей и новости
Post.objects.all().delete()  # Очищаем старые посты
post1 = Post.objects.create(author=author1, post_type=Post.ARTICLE, title='Первая статья', content='Текст первой статьи ' * 10)
post2 = Post.objects.create(author=author2, post_type=Post.ARTICLE, title='Вторая статья', content='Текст второй статьи ' * 10)
post3 = Post.objects.create(author=author1, post_type=Post.NEWS, title='Новость дня', content='Текст новости ' * 10)
print("Статьи созданы")

# 5. Добавление категорий к постам
PostCategory.objects.all().delete()  # Очищаем старые связи
PostCategory.objects.create(post=post1, category=cat1)
PostCategory.objects.create(post=post1, category=cat2)
PostCategory.objects.create(post=post2, category=cat3)
PostCategory.objects.create(post=post3, category=cat4)
PostCategory.objects.create(post=post3, category=cat1)
print("Категории добавлены к постам")

# 6. Создание комментариев
Comment.objects.all().delete()  # Очищаем старые комментарии
comment1 = Comment.objects.create(post=post1, user=user1, text='Отличная статья!')
comment2 = Comment.objects.create(post=post1, user=user2, text='Интересно!')
comment3 = Comment.objects.create(post=post2, user=user1, text='Спасибо!')
comment4 = Comment.objects.create(post=post3, user=user2, text='Ждем продолжения!')
print("Комментарии созданы")

# 7. Корректировка рейтингов
post1.like(); post1.like(); post1.dislike()
post2.like()
post3.like(); post3.like(); post3.like()

comment1.like(); comment1.like()
comment2.dislike()
comment3.like()
comment4.like(); comment4.like()
print("Рейтинги скорректированы")

# 8. Обновление рейтингов авторов
author1.update_rating()
author2.update_rating()
print("Рейтинги авторов обновлены")

# 9. Лучший пользователь
best_author = Author.objects.order_by('-rating').first()
print(f"Лучший автор: {best_author.user.username}, рейтинг: {best_author.rating}")

# 10. Лучшая статья
best_post = Post.objects.order_by('-rating').first()
print(f"Лучшая статья: {best_post.title}, рейтинг: {best_post.rating}")

print("=== Завершено ===")