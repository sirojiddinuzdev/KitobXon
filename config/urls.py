"""
URL configuration for config project.
"""
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from books.api import KitobViewSet, SorovViewSet, SevimliListAPI
from accounts.api import (
    RegisterAPI, LoginAPI, MeAPI, ProfilMeAPI, BildirishnomaViewSet,TasdiqlashAPI
)

# REST API router
router = DefaultRouter()
router.register('kitoblar', KitobViewSet, basename='api-kitob')
router.register('sorovlar', SorovViewSet, basename='api-sorov')
router.register('bildirishnomalar', BildirishnomaViewSet, basename='api-bildirishnoma')

api_urlpatterns = [
    path('auth/register/', RegisterAPI.as_view(), name='api-register'),
    path('auth/tasdiqlash/', TasdiqlashAPI.as_view(), name='api-tasdiqlash'),
    path('auth/login/', LoginAPI.as_view(), name='api-login'),
    path('auth/me/', MeAPI.as_view(), name='api-me'),
    path('profil/', ProfilMeAPI.as_view(), name='api-profil'),
    path('sevimlilar/', SevimliListAPI.as_view(), name='api-sevimlilar'),
    path('', include(router.urls)),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('books/', include('books.urls')),
    path('accounts/', include('accounts.urls')),
    path('', lambda request: redirect('kitoblar-royhati')),

    # REST API
    path('api/', include(api_urlpatterns)),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
