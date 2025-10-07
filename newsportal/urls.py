from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('news/', include('news.urls')),
    path('accounts/', include('allauth.urls')),  # Allauth URLs
    path('', RedirectView.as_view(url='/news/')),  # Перенаправление с корня на /news/
]