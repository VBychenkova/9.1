#команда python manage.py delete_news_from_category "Образование"

from django.core.management.base import BaseCommand
from news.models import Post, Category


class Command(BaseCommand):
    help = 'Удаляет новости/статьи из категории по названию или ID'

    def add_arguments(self, parser):
        parser.add_argument('category', help='Название категории или ID')
        parser.add_argument(
            '--post-type',
            type=str,
            choices=['news', 'articles', 'all'],
            default='news',
            help='Тип постов: news (новости), articles (статьи), all (все)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Удалить без подтверждения'
        )

    def handle(self, *args, **options):
        category_input = options['category']
        post_type = options['post_type']
        force = options['force']

        try:
            # Пытаемся найти категорию по ID или названию
            if category_input.isdigit():
                category = Category.objects.get(id=int(category_input))
            else:
                category = Category.objects.get(name=category_input)

            # Определяем тип постов для удаления
            if post_type == 'news':
                posts_query = Post.objects.filter(categories=category, post_type='NW')
                post_type_text = 'новости'
            elif post_type == 'articles':
                posts_query = Post.objects.filter(categories=category, post_type='AR')
                post_type_text = 'статьи'
            else:  # all
                posts_query = Post.objects.filter(categories=category)
                post_type_text = 'постов'

            # Считаем посты перед удалением
            posts_count = posts_query.count()

            if posts_count == 0:
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠️ В категории "{category.name}" нет {post_type_text} для удаления'
                    )
                )
                return

            # Запрос подтверждения (если не указан --force)
            if not force:
                self.stdout.write(
                    self.style.WARNING(
                        f'📊 Найдено {posts_count} {post_type_text} в категории "{category.name}"'
                    )
                )
                answer = input(f'❓ Вы уверены, что хотите удалить их? (yes/no): ')

                if answer.lower() != 'yes':
                    self.stdout.write(self.style.ERROR('❌ Отменено'))
                    return

            # Удаляем посты
            deleted_count, _ = posts_query.delete()

            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Успешно удалено {deleted_count} {post_type_text} из категории "{category.name}"'
                )
            )

        except Category.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ Категория "{category_input}" не найдена'))
            self.show_available_categories()

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Произошла ошибка: {e}'))

    def show_available_categories(self):
        """Показывает доступные категории"""
        self.stdout.write('\n📁 Доступные категории:')
        categories = [
            ('Спорт', 17),
            ('Политика', 18),
            ('Образование', 19),
            ('Технологии', 20)
        ]

        for name, id in categories:
            # Проверяем существует ли категория в базе
            try:
                category = Category.objects.get(id=id)
                news_count = Post.objects.filter(categories=category, post_type='NW').count()
                articles_count = Post.objects.filter(categories=category, post_type='AR').count()
                self.stdout.write(f'   - {name} (ID: {id}) | 📰 Новостей: {news_count} | 📝 Статей: {articles_count}')
            except Category.DoesNotExist:
                self.stdout.write(f'   - {name} (ID: {id}) | ❌ Не найдена в базе')