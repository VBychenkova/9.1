from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.shortcuts import redirect
from .models import Post, Author, Category, Subscription
from .forms import PostForm
from .filters import NewsFilter
from django.views.generic import TemplateView
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator


# Главная страница - кэшируем на 1 минуту
@method_decorator(cache_page(60), name='dispatch')
class HomePageView(TemplateView):
    template_name = 'news/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['latest_news'] = Post.objects.filter(post_type='NW').order_by('-created_at')[:3]
        except Exception as e:
            context['latest_news'] = []
            print(f"Ошибка при получении новостей: {e}")
        return context


# Список новостей - кэшируем на 1 минуту
@method_decorator(cache_page(60), name='dispatch')
class NewsList(ListView):
    model = Post
    template_name = 'news/news_list.html'
    context_object_name = 'posts'
    ordering = ['-created_at']
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем информацию о том, является ли пользователь автором
        context['is_author'] = self.request.user.groups.filter(
            name='authors').exists() if self.request.user.is_authenticated else False
        return context

# Детальная страница новости - кэшируем на 5 минут
@method_decorator(cache_page(300), name='dispatch')
class NewsDetail(DetailView):
    model = Post
    template_name = 'news/news_detail.html'
    context_object_name = 'news'

# Поиск новостей - НЕ кэшируем, так как это динамический запрос
def news_search(request):
    news_list = Post.objects.filter(post_type='NW').order_by('-created_at')
    news_filter = NewsFilter(request.GET, queryset=news_list)

    return render(request, 'news/news_search.html', {
        'filter': news_filter,
        'news': news_filter.qs
    })


# Создание, редактирование и удаление - НЕ кэшируем, так как требуют аутентификации
class NewsCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post',)
    form_class = PostForm
    model = Post
    template_name = 'news/news_edit.html'
    success_url = reverse_lazy('news_list')
    login_url = '/accounts/login/'

    def dispatch(self, request, *args, **kwargs):
        # Проверяем, что пользователь в группе authors
        if not request.user.groups.filter(name='authors').exists():
            messages.error(request, "Только авторы могут создавать новости. Станьте автором!")
            return redirect('news_list')

        # Проверяем лимит публикаций
        if not self.can_publish_today(request.user):
            messages.error(
                request,
                'Вы превысили лимит публикаций! Нельзя публиковать более 3 новостей/статей в сутки.'
            )
            return redirect('news_list')

        return super().dispatch(request, *args, **kwargs)

    def can_publish_today(self, user):
        """Проверяет, может ли пользователь опубликовать еще одну запись сегодня"""
        # Получаем начало текущих суток
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

        # Считаем количество постов пользователя за сегодня
        today_posts_count = Post.objects.filter(
            author__user=user,
            created_at__gte=today_start
        ).count()

        return today_posts_count < 3

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Добавляем информацию о лимите публикаций
        if self.request.user.is_authenticated:
            today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_posts_count = Post.objects.filter(
                author__user=self.request.user,
                created_at__gte=today_start
            ).count()
            context['remaining_posts'] = 3 - today_posts_count
        else:
            context['remaining_posts'] = 0

        return context

    def form_valid(self, form):
        # Проверяем лимит еще раз перед сохранением
        if not self.can_publish_today(self.request.user):
            messages.error(
                self.request,
                'Вы превысили лимит публикаций! Нельзя публиковать более 3 новостей/статей в сутки.'
            )
            return redirect('news_list')

        post = form.save(commit=False)
        post.post_type = 'NW'

        try:
            author = Author.objects.get(user=self.request.user)
        except Author.DoesNotExist:
            author = Author.objects.create(user=self.request.user)

        post.author = author

        # Сохраняем пост
        response = super().form_valid(form)

        # Показываем сообщение об успехе с информацией о лимите
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_posts_count = Post.objects.filter(
            author__user=self.request.user,
            created_at__gte=today_start
        ).count()

        remaining_posts = 3 - today_posts_count
        messages.success(
            self.request,
            f'Новость успешно создана! Сегодня вы можете опубликовать еще {remaining_posts} записей.'
        )

        return response


class NewsUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = ('news.change_post',)
    form_class = PostForm
    model = Post
    template_name = 'news/news_edit.html'
    login_url = '/accounts/login/'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()

        # Проверяем, что пользователь в группе authors
        if not request.user.groups.filter(name='authors').exists():
            messages.error(request, "Только авторы могут редактировать новости. Станьте автором!")
            return redirect('news_list')

        # Проверяем, что пост является новостью
        if obj.post_type != 'NW':
            messages.error(request, "Вы можете редактировать только новости")
            return redirect('news_list')

        # Разрешаем доступ если пользователь - автор ИЛИ суперпользователь
        if obj.author.user != request.user and not request.user.is_superuser:
            messages.error(request, "Вы не можете редактировать эту новость")
            return redirect('news_list')

        return super().dispatch(request, *args, **kwargs)


class NewsDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = ('news.delete_post',)
    model = Post
    template_name = 'news/news_delete.html'
    success_url = reverse_lazy('news_list')
    login_url = '/accounts/login/'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()

        # Проверяем, что пользователь в группе authors
        if not request.user.groups.filter(name='authors').exists():
            messages.error(request, "Только авторы могут удалять новости. Станьте автором!")
            return redirect('news_list')

        # Проверяем, что пост является новостью
        if obj.post_type != 'NW':
            messages.error(request, "Вы можете удалять только новости")
            return redirect('news_list')

        # Разрешаем доступ если пользователь - автор ИЛИ суперпользователь
        if obj.author.user != request.user and not request.user.is_superuser:
            messages.error(request, "Вы не можете удалить эту новость")
            return redirect('news_list')

        return super().dispatch(request, *args, **kwargs)


class ArticleCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post',)
    form_class = PostForm
    model = Post
    template_name = 'news/article_edit.html'
    login_url = '/accounts/login/'

    def dispatch(self, request, *args, **kwargs):
        # Проверяем, что пользователь в группе authors
        if not request.user.groups.filter(name='authors').exists():
            messages.error(request, "Только авторы могут создавать статьи. Станьте автором!")
            return redirect('news_list')

        # Проверяем лимит публикаций
        if not self.can_publish_today(request.user):
            messages.error(
                request,
                'Вы превысили лимит публикаций! Нельзя публиковать более 3 новостей/статей в сутки.'
            )
            return redirect('news_list')

        return super().dispatch(request, *args, **kwargs)

    def can_publish_today(self, user):
        """Проверяет, может ли пользователь опубликовать еще одну запись сегодня"""
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

        today_posts_count = Post.objects.filter(
            author__user=user,
            created_at__gte=today_start
        ).count()

        return today_posts_count < 3

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Добавляем информацию о лимите публикаций
        if self.request.user.is_authenticated:
            today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_posts_count = Post.objects.filter(
                author__user=self.request.user,
                created_at__gte=today_start
            ).count()
            context['remaining_posts'] = 3 - today_posts_count
        else:
            context['remaining_posts'] = 0

        return context

    def form_valid(self, form):
        # Проверяем лимит еще раз перед сохранением
        if not self.can_publish_today(self.request.user):
            messages.error(
                self.request,
                'Вы превысили лимит публикаций! Нельзя публиковать более 3 новостей/статей в сутки.'
            )
            return redirect('news_list')

        post = form.save(commit=False)
        post.post_type = 'AR'

        author, created = Author.objects.get_or_create(user=self.request.user)
        post.author = author

        response = super().form_valid(form)

        # Показываем сообщение об успехе с информацией о лимите
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_posts_count = Post.objects.filter(
            author__user=self.request.user,
            created_at__gte=today_start
        ).count()

        remaining_posts = 3 - today_posts_count
        messages.success(
            self.request,
            f'Статья успешно создана! Сегодня вы можете опубликовать еще {remaining_posts} записей.'
        )

        return response


class ArticleUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = ('news.change_post',)
    form_class = PostForm
    model = Post
    template_name = 'news/article_edit.html'
    login_url = '/accounts/login/'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()

        # Проверяем, что пользователь в группе authors
        if not request.user.groups.filter(name='authors').exists():
            messages.error(request, "Только авторы могут редактировать статьи. Станьте автором!")
            return redirect('news_list')

        # Проверяем, что пост является статьей
        if obj.post_type != 'AR':
            messages.error(request, "Вы можете редактировать только статьи")
            return redirect('news_list')

        # Разрешаем доступ если пользователь - автор ИЛИ суперпользователь
        if obj.author.user != request.user and not request.user.is_superuser:
            messages.error(request, "Вы не можете редактировать эту статью")
            return redirect('news_list')

        return super().dispatch(request, *args, **kwargs)


class ArticleDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = ('news.delete_post',)
    model = Post
    template_name = 'news/article_delete.html'
    success_url = reverse_lazy('news_list')
    login_url = '/accounts/login/'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()

        # Проверяем, что пользователь в группе authors
        if not request.user.groups.filter(name='authors').exists():
            messages.error(request, "Только авторы могут удалять статьи. Станьте автором!")
            return redirect('news_list')

        # Проверяем, что пост является статьей
        if obj.post_type != 'AR':
            messages.error(request, "Вы можете удалять только статьи")
            return redirect('news_list')

        # Разрешаем доступ если пользователь - автор ИЛИ суперпользователь
        if obj.author.user != request.user and not request.user.is_superuser:
            messages.error(request, "Вы не можете удалить эту статью")
            return redirect('news_list')

        return super().dispatch(request, *args, **kwargs)


@method_decorator(cache_page(20), name='dispatch')
class ArticleList(ListView):
    model = Post
    template_name = 'news/article_list.html'
    context_object_name = 'articles'
    ordering = ['-created_at']
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(post_type='AR')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_author'] = self.request.user.groups.filter(
            name='authors').exists() if self.request.user.is_authenticated else False
        return context

@method_decorator(cache_page(300), name='dispatch')
class ArticleDetail(DetailView):
    model = Post
    template_name = 'news/article_detail.html'
    context_object_name = 'article'

    def get_queryset(self):
        return Post.objects.filter(post_type='AR')

# Функции, требующие аутентификации - НЕ кэшируем
@login_required
def become_author(request):
    user = request.user
    authors_group = Group.objects.get(name='authors')

    if request.method == 'POST':
        if not user.groups.filter(name='authors').exists():
            authors_group.user_set.add(user)
            messages.success(request, 'Поздравляем! Теперь вы автор!')
            return redirect('news_list')
        else:
            messages.info(request, 'Вы уже являетесь автором')
            return redirect('news_list')

    # Проверяем, является ли пользователь уже автором
    is_author = user.groups.filter(name='authors').exists()

    return render(request, 'news/become_author.html', {
        'is_author': is_author
    })


@login_required
def subscribe_to_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    # Проверяем, не подписан ли уже пользователь
    if not Subscription.objects.filter(user=request.user, category=category).exists():
        Subscription.objects.create(user=request.user, category=category)
        messages.success(request, f'Вы подписались на категорию "{category.name}"')
    else:
        messages.info(request, f'Вы уже подписаны на категорию "{category.name}"')

    return redirect('news_list')


@login_required
def unsubscribe_from_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    subscription = Subscription.objects.filter(user=request.user, category=category)
    if subscription.exists():
        subscription.delete()
        messages.success(request, f'Вы отписались от категории "{category.name}"')
    else:
        messages.info(request, f'Вы не были подписаны на категорию "{category.name}"')

    return redirect('news_list')


@login_required
def my_subscriptions(request):
    subscriptions = Subscription.objects.filter(user=request.user)
    return render(request, 'news/my_subscriptions.html', {
        'subscriptions': subscriptions
    })

