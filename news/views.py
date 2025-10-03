from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.shortcuts import redirect
from .models import Post, Author, Category
from .forms import PostForm
from .filters import NewsFilter
from django.views.generic import TemplateView


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

class NewsList(ListView):
    model = Post
    template_name = 'news/news_list.html'
    context_object_name = 'posts'  # меняем на posts
    ordering = ['-created_at']
    paginate_by = 10

    def get_queryset(self):
        # Показываем и новости и статьи
        return Post.objects.all()


class NewsDetail(DetailView):
    model = Post
    template_name = 'news/news_detail.html'
    context_object_name = 'news'


def news_search(request):
    news_list = Post.objects.filter(post_type='NW').order_by('-created_at')
    news_filter = NewsFilter(request.GET, queryset=news_list)

    return render(request, 'news/news_search.html', {
        'filter': news_filter,
        'news': news_filter.qs
    })


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
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.post_type = 'NW'

        try:
            # Пытаемся найти автора для текущего пользователя
            author = Author.objects.get(user=self.request.user)
        except Author.DoesNotExist:
            # Если автора нет - создаем его
            author = Author.objects.create(user=self.request.user)

        post.author = author
        return super().form_valid(form)


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
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.post_type = 'AR'  # автоматически ставим тип "статья"

        # Получаем или создаем автора для текущего пользователя
        author, created = Author.objects.get_or_create(user=self.request.user)
        post.author = author

        return super().form_valid(form)


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