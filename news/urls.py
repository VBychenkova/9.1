from django.urls import path, include
from . import views

urlpatterns = [
    # Главная страница
    path('i18n/', include('django.conf.urls.i18n')),
    path('', views.NewsList.as_view(), name='news_list'),
    path('home/', views.HomePageView.as_view(), name='home'),

    # Новости
    path('news/', views.NewsList.as_view(), name='news_list'),
    path('news/<int:pk>/', views.NewsDetail.as_view(), name='news_detail'),
    path('news/create/', views.NewsCreate.as_view(), name='news_create'),
    path('news/<int:pk>/edit/', views.NewsUpdate.as_view(), name='news_update'),
    path('news/<int:pk>/delete/', views.NewsDelete.as_view(), name='news_delete'),

    # Статьи
    path('articles/', views.ArticleList.as_view(), name='article_list'),
    path('articles/<int:pk>/', views.ArticleDetail.as_view(), name='article_detail'),
    path('articles/create/', views.ArticleCreate.as_view(), name='article_create'),
    path('articles/<int:pk>/edit/', views.ArticleUpdate.as_view(), name='article_update'),
    path('articles/<int:pk>/delete/', views.ArticleDelete.as_view(), name='article_delete'),

    # Поиск
    path('search/', views.news_search, name='news_search'),

    # Авторство и подписки
    path('become-author/', views.become_author, name='become_author'),
    path('subscribe/<int:category_id>/', views.subscribe_to_category, name='subscribe_to_category'),
    path('unsubscribe/<int:category_id>/', views.unsubscribe_from_category, name='unsubscribe_from_category'),
    path('my-subscriptions/', views.my_subscriptions, name='my_subscriptions'),
]