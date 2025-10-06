from django.urls import path
from . import views
from .views import become_author, HomePageView

urlpatterns = [
    # Главная страница
    path('', HomePageView.as_view(), name='home'),

    # Список новостей
    path('news/', views.NewsList.as_view(), name='news_list'),

    # Детали новости/статьи
    path('news/<int:pk>/', views.NewsDetail.as_view(), name='news_detail'),

    # Поиск
    path('news/search/', views.news_search, name='news_search'),

    # Создание новостей
    path('news/create/', views.NewsCreate.as_view(), name='news_create'),
    path('news/<int:pk>/edit/', views.NewsUpdate.as_view(), name='news_edit'),
    path('news/<int:pk>/delete/', views.NewsDelete.as_view(), name='news_delete'),

    # Создание статей
    path('articles/create/', views.ArticleCreate.as_view(), name='article_create'),
    path('articles/<int:pk>/edit/', views.ArticleUpdate.as_view(), name='article_edit'),
    path('articles/<int:pk>/delete/', views.ArticleDelete.as_view(), name='article_delete'),

    # Стать автором
    path('become-author/', views.become_author, name='become_author'),

    path('category/<int:category_id>/subscribe/', views.subscribe_to_category, name='subscribe_category'),
    path('category/<int:category_id>/unsubscribe/', views.unsubscribe_from_category, name='unsubscribe_category'),
    path('my-subscriptions/', views.my_subscriptions, name='my_subscriptions'),

]