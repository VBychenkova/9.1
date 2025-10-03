from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    #path('news/', include('news.urls')),
    path('', include('news.urls')),
    #path('sign/', include('sign.urls')), # Убираем пути для sign и protect
    path('accounts/', include('allauth.urls')),  # Allauth URLs
]