"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.views.static import serve

from core import settings
from users.views import GoogleLoginAPIView


def trigger_error(request):
    division_by_zero = 1 / 0


urlpatterns = [
    path("api/v1/docs/", admin.site.urls),
    path("api/v1/common/", include("common.urls")),
    path("api/v1/products/", include("products.urls")),
    path("api/v1/auth/", include("users.urls")),
    path("api/v1/orders/", include("orders.urls")),
    # Social Auth (Google, etc.)
    path("api/v1/auth/social/", include("social_django.urls"), name="social"),
    path(
        "api/v1/auth/social/google/", GoogleLoginAPIView.as_view(), name="google_auth"
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0]
    )
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += [
        re_path(
            r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}
        ),
        re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    ]
