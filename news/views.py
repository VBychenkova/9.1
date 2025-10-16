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
from .models import Post, Author, Category, Subscription, Article, News
from .forms import PostForm, ArticleForm, NewsForm
from django_filters.views import FilterView
from .filters import NewsFilter, ArticleFilter
from django.views.generic import TemplateView
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _


def set_timezone(request):
    if request.method == 'POST':
        request.session['django_timezone'] = request.POST['timezone']
        messages.success(request, _('Timezone updated successfully!'))
        return redirect(request.META.get('HTTP_REFERER', '/'))
    return redirect('/')


# Список распространенных часовых поясов (можно расширить)
COMMON_TIMEZONES = [
    'UTC',
    'Europe/Moscow',
    'Europe/London',
    'Europe/Berlin',
    'Europe/Paris',
    'America/New_York',
    'America/Los_Angeles',
    'Asia/Tokyo',
    'Asia/Shanghai',
    'Australia/Sydney',
]


# Главная страница
class HomePageView(TemplateView):
    template_name = 'news/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['latest_news'] = Post.objects.filter(post_type='NW').order_by('-created_at')[:3]
        except Exception as e:
            context['latest_news'] = []
            print(f"Ошибка при получении новостей: {e}")

        # Добавляем контекст для времени и часовых поясов
        context['current_time'] = timezone.now()
        context['timezones'] = COMMON_TIMEZONES
        return context


# Список новостей
class NewsList(ListView):
    model = Post
    template_name = 'news/news_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(
            post_type='NW',
            is_published=True
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_author'] = self.request.user.groups.filter(
            name='authors').exists() if self.request.user.is_authenticated else False
        # Добавляем контекст для времени и часовых поясов
        context['current_time'] = timezone.now()
        context['timezones'] = COMMON_TIMEZONES
        # Добавляем общее количество для статистики
        context['total_news_count'] = Post.objects.filter(
            post_type='NW',
            is_published=True
        ).count()

        return context


# Детальная страница новости
class NewsDetail(DetailView):
    model = Post
    template_name = 'news/news_detail.html'
    context_object_name = 'news'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем контекст для времени и часовых поясов
        context['current_time'] = timezone.now()
        context['timezones'] = COMMON_TIMEZONES
        return context


# Создание новости
class NewsCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post',)
    form_class = PostForm
    model = Post
    template_name = 'news/news_edit.html'
    success_url = reverse_lazy('news_list')
    login_url = '/accounts/login/'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='authors').exists():
            messages.error(request, _("Only authors can create news. Become an author!"))
            return redirect('news_list')

        if not self.can_publish_today(request.user):
            messages.error(
                request,
                _('You have exceeded the publication limit! You cannot publish more than 3 news/articles per day.')
            )
            return redirect('news_list')

        return super().dispatch(request, *args, **kwargs)

    def can_publish_today(self, user):
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_posts_count = Post.objects.filter(
            author__user=user,
            created_at__gte=today_start
        ).count()
        return today_posts_count < 3

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_posts_count = Post.objects.filter(
                author__user=self.request.user,
                created_at__gte=today_start
            ).count()
            context['remaining_posts'] = 3 - today_posts_count
        else:
            context['remaining_posts'] = 0

        context['current_time'] = timezone.now()
        context['timezones'] = COMMON_TIMEZONES
        return context

    def form_valid(self, form):
        if not self.can_publish_today(self.request.user):
            messages.error(
                self.request,
                _('You have exceeded the publication limit! You cannot publish more than 3 news/articles per day.')
            )
            return redirect('news_list')

        post = form.save(commit=False)
        post.post_type = 'NW'

        try:
            author = Author.objects.get(user=self.request.user)
        except Author.DoesNotExist:
            author = Author.objects.create(user=self.request.user)

        post.author = author
        response = super().form_valid(form)

        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_posts_count = Post.objects.filter(
            author__user=self.request.user,
            created_at__gte=today_start
        ).count()

        remaining_posts = 3 - today_posts_count
        messages.success(
            self.request,
            _('News created successfully! Today you can publish %(remaining_posts)s more posts.') % {
                'remaining_posts': remaining_posts
            }
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

        if not request.user.groups.filter(name='authors').exists():
            messages.error(request, _("Only authors can edit news. Become an author!"))
            return redirect('news_list')

        if obj.post_type != 'NW':
            messages.error(request, _("You can only edit news"))
            return redirect('news_list')

        if obj.author.user != request.user and not request.user.is_superuser:
            messages.error(request, _("You cannot edit this news"))
            return redirect('news_list')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_time'] = timezone.now()
        context['timezones'] = COMMON_TIMEZONES
        return context


class NewsDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = ('news.delete_post',)
    model = Post
    template_name = 'news/news_delete.html'
    success_url = reverse_lazy('news_list')
    login_url = '/accounts/login/'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()

        if not request.user.groups.filter(name='authors').exists():
            messages.error(request, _("Only authors can delete news. Become an author!"))
            return redirect('news_list')

        if obj.post_type != 'NW':
            messages.error(request, _("You can only delete news"))
            return redirect('news_list')

        if obj.author.user != request.user and not request.user.is_superuser:
            messages.error(request, _("You cannot delete this news"))
            return redirect('news_list')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_time'] = timezone.now()
        context['timezones'] = COMMON_TIMEZONES
        return context


class ArticleCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post',)
    form_class = PostForm
    model = Post
    template_name = 'news/article_edit.html'
    login_url = '/accounts/login/'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='authors').exists():
            messages.error(request, _("Only authors can create articles. Become an author!"))
            return redirect('news_list')

        if not self.can_publish_today(request.user):
            messages.error(
                request,
                _('You have exceeded the publication limit! You cannot publish more than 3 news/articles per day.')
            )
            return redirect('news_list')

        return super().dispatch(request, *args, **kwargs)

    def can_publish_today(self, user):
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_posts_count = Post.objects.filter(
            author__user=user,
            created_at__gte=today_start
        ).count()
        return today_posts_count < 3

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_posts_count = Post.objects.filter(
                author__user=self.request.user,
                created_at__gte=today_start
            ).count()
            context['remaining_posts'] = 3 - today_posts_count
        else:
            context['remaining_posts'] = 0

        context['current_time'] = timezone.now()
        context['timezones'] = COMMON_TIMEZONES
        return context

    def form_valid(self, form):
        if not self.can_publish_today(self.request.user):
            messages.error(
                self.request,
                _('You have exceeded the publication limit! You cannot publish more than 3 news/articles per day.')
            )
            return redirect('news_list')

        post = form.save(commit=False)
        post.post_type = 'AR'

        author, created = Author.objects.get_or_create(user=self.request.user)
        post.author = author
        response = super().form_valid(form)

        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_posts_count = Post.objects.filter(
            author__user=self.request.user,
            created_at__gte=today_start
        ).count()

        remaining_posts = 3 - today_posts_count
        messages.success(
            self.request,
            _('Article created successfully! Today you can publish %(remaining_posts)s more posts.') % {
                'remaining_posts': remaining_posts
            }
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

        if not request.user.groups.filter(name='authors').exists():
            messages.error(request, _("Only authors can edit articles. Become an author!"))
            return redirect('news_list')

        if obj.post_type != 'AR':
            messages.error(request, _("You can only edit articles"))
            return redirect('news_list')

        if obj.author.user != request.user and not request.user.is_superuser:
            messages.error(request, _("You cannot edit this article"))
            return redirect('news_list')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_time'] = timezone.now()
        context['timezones'] = COMMON_TIMEZONES
        return context


class ArticleDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = ('news.delete_post',)
    model = Post
    template_name = 'news/article_delete.html'
    success_url = reverse_lazy('news_list')
    login_url = '/accounts/login/'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()

        if not request.user.groups.filter(name='authors').exists():
            messages.error(request, _("Only authors can delete articles. Become an author!"))
            return redirect('news_list')

        if obj.post_type != 'AR':
            messages.error(request, _("You can only delete articles"))
            return redirect('news_list')

        if obj.author.user != request.user and not request.user.is_superuser:
            messages.error(request, _("You cannot delete this article"))
            return redirect('news_list')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_time'] = timezone.now()
        context['timezones'] = COMMON_TIMEZONES
        return context


class ArticleList(ListView):
    model = Post
    template_name = 'news/article_list.html'
    context_object_name = 'articles'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(post_type='AR').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_author'] = self.request.user.groups.filter(
            name='authors').exists() if self.request.user.is_authenticated else False
        context['current_time'] = timezone.now()
        context['timezones'] = COMMON_TIMEZONES
        return context


class ArticleDetail(DetailView):
    model = Post
    template_name = 'news/article_detail.html'
    context_object_name = 'article'

    def get_queryset(self):
        return Post.objects.filter(post_type='AR')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем контекст для времени и часовых поясов
        context['current_time'] = timezone.now()
        context['timezones'] = COMMON_TIMEZONES

        # Добавляем информацию об авторе для шаблона
        context['is_author'] = self.request.user.groups.filter(
            name='authors').exists() if self.request.user.is_authenticated else False

        return context


def news_search(request):
    news_list = Post.objects.filter(post_type='NW').order_by('-created_at')
    query = request.GET.get('q', '')
    if query:
        news_list = news_list.filter(title__icontains=query)

    return render(request, 'news/news_search.html', {
        'news': news_list,
        'query': query,
        'current_time': timezone.now(),
        'timezones': COMMON_TIMEZONES,
    })


@login_required
def become_author(request):
    user = request.user

    if request.method == 'POST':
        # Создаем группу authors если её нет
        authors_group, created = Group.objects.get_or_create(name='authors')

        if not user.groups.filter(name='authors').exists():
            # Добавляем пользователя в группу authors
            authors_group.user_set.add(user)

            # Создаем запись Author если её нет
            from .models import Author
            Author.objects.get_or_create(user=user)

            messages.success(request,
                             _('Congratulations! You are now an author! You can now create news and articles.'))
            return redirect('news_list')
        else:
            messages.info(request, _('You are already an author'))
            return redirect('news_list')

    # Проверяем, является ли пользователь уже автором
    is_author = user.groups.filter(name='authors').exists()

    return render(request, 'news/become_author.html', {
        'is_author': is_author,
        'current_time': timezone.now(),
        'timezones': COMMON_TIMEZONES,
    })


@login_required
def subscribe_to_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if not Subscription.objects.filter(user=request.user, category=category).exists():
        Subscription.objects.create(user=request.user, category=category)
        messages.success(request, _('You have subscribed to category "%(category_name)s"') % {
            'category_name': category.name
        })
    else:
        messages.info(request, _('You are already subscribed to category "%(category_name)s"') % {
            'category_name': category.name
        })

    return redirect('news_list')


@login_required
def unsubscribe_from_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    subscription = Subscription.objects.filter(user=request.user, category=category)
    if subscription.exists():
        subscription.delete()
        messages.success(request, _('You have unsubscribed from category "%(category_name)s"') % {
            'category_name': category.name
        })
    else:
        messages.info(request, _('You were not subscribed to category "%(category_name)s"') % {
            'category_name': category.name
        })

    return redirect('news_list')


@login_required
def my_subscriptions(request):
    subscriptions = Subscription.objects.filter(user=request.user)
    return render(request, 'news/my_subscriptions.html', {
        'subscriptions': subscriptions,
        'current_time': timezone.now(),
        'timezones': COMMON_TIMEZONES,
    })