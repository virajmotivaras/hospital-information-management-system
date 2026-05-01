from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.contrib.auth.decorators import login_required
from django.urls import include, path
from django.views.generic import TemplateView
from api.auth_views import app_login


urlpatterns = [
    path("", login_required(TemplateView.as_view(template_name="index.html")), name="home"),
    path("login/", app_login, name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.FRONTEND_DIR)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
