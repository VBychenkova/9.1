import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newsportal.settings')
django.setup()

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from news.models import Post


def create_authors_group():
    # Создаем группу authors
    group, created = Group.objects.get_or_create(name='authors')

    if created:
        print("Группа 'authors' создана")

        # Добавляем разрешения для группы authors
        content_type = ContentType.objects.get_for_model(Post)

        # Базовые разрешения для авторов
        permissions = [
            'add_post', 'change_post', 'delete_post',
            'view_post'
        ]

        for perm in permissions:
            permission = Permission.objects.get(
                content_type=content_type,
                codename=perm
            )
            group.permissions.add(permission)
            print(f"Добавлено разрешение: {perm}")

        print("Все разрешения добавлены в группу 'authors'")
    else:
        print("Группа 'authors' уже существует")


if __name__ == '__main__':
    create_authors_group()