import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newsportal.settings')
django.setup()

from news.models import Author, Category, Post, Comment

print("=" * 50)
print("ПРОВЕРКА СОЗДАННЫХ ДАННЫХ")
print("=" * 50)

# Проверка количества
print(f"Авторы: {Author.objects.count()}")
print(f"Категории: {Category.objects.count()}")
print(f"Статьи/новости: {Post.objects.count()}")
print(f"Комментарии: {Comment.objects.count()}")

print("\n--- РЕЙТИНГИ АВТОРОВ ---")
authors = Author.objects.all()
for author in authors:
    print(f"{author.user.username}: {author.rating}")

print("\n--- ЛУЧШАЯ СТАТЬЯ ---")
best_post = Post.objects.order_by('-rating').first()
if best_post:
    print(f"Заголовок: {best_post.title}")
    print(f"Автор: {best_post.author.user.username}")
    print(f"Рейтинг: {best_post.rating}")
    print(f"Превью: {best_post.preview()}")

    print("\n--- КОММЕНТАРИИ К СТАТЬЕ ---")
    comments = Comment.objects.filter(post=best_post)
    for i, comment in enumerate(comments, 1):
        print(f"{i}. {comment.user.username} (рейтинг: {comment.rating}):")
        print(f"   {comment.text}")
        print(f"   Дата: {comment.created_at}")
else:
    print("Статьи не найдены")

print("\n" + "=" * 50)
print("ПРОВЕРКА ЗАВЕРШЕНА")