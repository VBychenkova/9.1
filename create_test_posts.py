import os
import django
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newsportal.settings')
django.setup()

from django.contrib.auth.models import User
from news.models import Author, Category, Post, PostCategory
from django.utils.translation import gettext as _


def create_test_data():
    print("=== Создание тестовых данных ===")

    # Создаем тестового пользователя и автора
    user, created = User.objects.get_or_create(
        username='test_author',
        defaults={
            'email': 'author@newsportal.com',
            'first_name': 'Тест',
            'last_name': 'Авторов'
        }
    )
    if created:
        user.set_password('testpassword123')
        user.save()
        print("✅ Создан пользователь: test_author")

    # Создаем автора
    author, created = Author.objects.get_or_create(user=user)
    if created:
        print("✅ Создан автор")

    # Получаем или создаем категории
    categories_data = [
        ('Политика', 'Новости о политике и государстве'),
        ('Экономика', 'Финансовые и бизнес новости'),
        ('Технологии', 'IT, гаджеты и инновации'),
        ('Спорт', 'Спортивные события и результаты'),
        ('Культура', 'Искусство, кино и музыка'),
    ]

    categories = {}
    for name, description in categories_data:
        category, created = Category.objects.get_or_create(name=name)
        categories[name] = category
        if created:
            print(f"✅ Создана категория: {name}")

    # Тестовые новости (post_type = 'NW')
    news_posts = [
        {
            'title': 'Встреча лидеров стран G20 завершилась подписанием соглашения',
            'content': '''Сегодня в столице завершилась двухдневная встреча лидеров стран G20, 
            в ходе которой были обсуждены ключевые вопросы мировой экономики и международной безопасности. 
            По итогам саммита было подписано совместное заявление, направленное на укрепление 
            сотрудничества в области торговли и борьбы с изменением климата. Участники также 
            договорились о создании новой рабочей группы по цифровой экономике.''',
            'categories': ['Политика', 'Экономика'],
            'rating': 45,
            'days_ago': 1
        },
        {
            'title': 'Новый технологический прорыв в области искусственного интеллекта',
            'content': '''Ученые объявили о значительном прогрессе в разработке систем 
            искусственного интеллекта. Новая нейросеть демонстрирует беспрецедентные 
            способности в обработке естественного языка и решении сложных задач. 
            Разработчики утверждают, что их технология может революционизировать 
            множество отраслей - от медицины до образования.''',
            'categories': ['Технологии', 'Наука'],
            'rating': 78,
            'days_ago': 2
        },
        {
            'title': 'Национальная сборная одержала победу в чемпионате мира',
            'content': '''В захватывающем финальном матче национальная сборная по футболу 
            одержала победу со счетом 3:2. Решающий гол был забит на последней минуте 
            дополнительного времени. Тысячи болельщиков по всей стране вышли на улицы 
            праздновать эту историческую победу. Тренер команды отметил выдающуюся 
            игру всех участников.''',
            'categories': ['Спорт'],
            'rating': 120,
            'days_ago': 0
        },
        {
            'title': 'Крупная кибератака поразила финансовые учреждения',
            'content': '''Сегодня утром несколько крупных банков и финансовых компаний 
            столкнулись с масштабной кибератакой. Эксперты по кибербезопасности 
            работают над восстановлением систем и расследованием инцидента. 
            Пользователям рекомендуется сменить пароли и внимательно следить 
            за своими счетами.''',
            'categories': ['Технологии', 'Экономика'],
            'rating': 34,
            'days_ago': 1
        },
        {
            'title': 'Открытие нового культурного центра в центре города',
            'content': '''Сегодня состоялось торжественное открытие нового 
            многофункционального культурного центра. В церемонии приняли участие 
            известные деятели искусства, музыканты и представители городской администрации. 
            Центр будет включать в себя выставочные залы, концертный зал и образовательные пространства.''',
            'categories': ['Культура'],
            'rating': 23,
            'days_ago': 3
        }
    ]

    # Тестовые статьи (post_type = 'AR')
    article_posts = [
        {
            'title': 'Анализ текущей экономической ситуации и прогнозы на будущее',
            'content': '''В данной статье мы подробно анализируем текущее состояние 
            мировой экономики и рассматриваем основные тенденции, которые будут 
            определять ее развитие в ближайшие годы. Особое внимание уделяется 
            влиянию цифровизации, изменению потребительского поведения и 
            геополитическим факторам. Эксперты сходятся во мнении, что...''',
            'categories': ['Экономика'],
            'rating': 67,
            'days_ago': 5
        },
        {
            'title': 'Будущее искусственного интеллекта: возможности и вызовы',
            'content': '''Искусственный интеллект продолжает трансформировать 
            нашу жизнь, но какие перспективы и риски несет эта технология? 
            В статье рассматриваются этические вопросы, потенциальное влияние 
            на рынок труда и возможности для научного прогресса. Автор предлагает 
            roadmap для ответственного развития ИИ.''',
            'categories': ['Технологии', 'Наука'],
            'rating': 89,
            'days_ago': 7
        },
        {
            'title': 'Роль спорта в формировании здорового общества',
            'content': '''Физическая активность и спорт играют crucial роль 
            в поддержании здоровья населения. В статье анализируются данные 
            исследований о влиянии регулярных занятий спортом на физическое 
            и ментальное здоровье, а также рассматриваются стратегии 
            популяризации активного образа жизни.''',
            'categories': ['Спорт', 'Здоровье'],
            'rating': 42,
            'days_ago': 10
        },
        {
            'title': 'Цифровая трансформация политических процессов',
            'content': '''Как технологии изменяют политическую коммуникацию 
            и процессы принятия решений? В статье исследуется влияние 
            социальных сетей, big data и алгоритмов на современную политику. 
            Автор рассматривает как положительные аспекты, так и потенциальные 
            риски цифровизации политической сферы.''',
            'categories': ['Политика', 'Технологии'],
            'rating': 55,
            'days_ago': 4
        },
        {
            'title': 'Современное искусство в эпоху цифровых технологий',
            'content': '''Цифровые технологии открывают новые горизонты 
            для художественного выражения. В статье рассматриваются такие 
            явления как NFT, цифровые инсталляции и виртуальная реальность 
            в искусстве. Как технологии меняют восприятие и создание 
            художественных произведений?''',
            'categories': ['Культура', 'Технологии'],
            'rating': 38,
            'days_ago': 6
        }
    ]

    created_posts = 0

    # Создаем новости
    print("\n=== Создание новостей ===")
    for news_data in news_posts:
        try:
            # Создаем пост с указанной датой
            created_date = timezone.now() - timedelta(days=news_data['days_ago'])

            post = Post.objects.create(
                author=author,
                post_type='NW',
                title=news_data['title'],
                content=news_data['content'],
                rating=news_data['rating'],
                is_published=True,
                created_at=created_date
            )

            # Добавляем категории
            for category_name in news_data['categories']:
                if category_name in categories:
                    PostCategory.objects.create(
                        post=post,
                        category=categories[category_name]
                    )

            created_posts += 1
            print(f"✅ Создана новость: {news_data['title']}")

        except Exception as e:
            print(f"❌ Ошибка при создании новости '{news_data['title']}': {e}")

    # Создаем статьи
    print("\n=== Создание статей ===")
    for article_data in article_posts:
        try:
            # Создаем пост с указанной датой
            created_date = timezone.now() - timedelta(days=article_data['days_ago'])

            post = Post.objects.create(
                author=author,
                post_type='AR',
                title=article_data['title'],
                content=article_data['content'],
                rating=article_data['rating'],
                is_published=True,
                created_at=created_date
            )

            # Добавляем категории
            for category_name in article_data['categories']:
                if category_name in categories:
                    PostCategory.objects.create(
                        post=post,
                        category=categories[category_name]
                    )

            created_posts += 1
            print(f"✅ Создана статья: {article_data['title']}")

        except Exception as e:
            print(f"❌ Ошибка при создании статьи '{article_data['title']}': {e}")

    # Статистика
    print(f"\n=== Статистика ===")
    print(f"Всего создано постов: {created_posts}")
    print(f"Новостей: {Post.objects.filter(post_type='NW').count()}")
    print(f"Статей: {Post.objects.filter(post_type='AR').count()}")
    print(f"Всего постов в базе: {Post.objects.count()}")
    print(f"Категорий: {Category.objects.count()}")

    # Информация для тестирования
    print(f"\n=== Информация для тестирования ===")
    print(f"Логин тестового автора: test_author")
    print(f"Пароль: testpassword123")
    print(f"URL новостей: http://127.0.0.1:8000/news/")
    print(f"URL статей: http://127.0.0.1:8000/articles/")


if __name__ == '__main__':
    create_test_data()