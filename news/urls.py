from django.urls import path
from . import views

urlpatterns = [
    path('', views.NewsList.as_view(), name='news_list'),
    path('<int:pk>/', views.NewsDetail.as_view(), name='news_detail'),
    path('search/', views.news_search, name='news_search'),

    # Новости
    path('create/', views.NewsCreate.as_view(), name='news_create'),
    path('<int:pk>/edit/', views.NewsUpdate.as_view(), name='news_edit'),
    path('<int:pk>/delete/', views.NewsDelete.as_view(), name='news_delete'),

    # Статьи
    path('articles/create/', views.ArticleCreate.as_view(), name='article_create'),
    path('articles/<int:pk>/edit/', views.ArticleUpdate.as_view(), name='article_edit'),
    path('articles/<int:pk>/delete/', views.ArticleDelete.as_view(), name='article_delete'),
]