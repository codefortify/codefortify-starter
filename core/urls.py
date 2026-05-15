import os
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


admin_path = (os.environ.get("CODEFORTIFY_DJANGO_ADMIN_PATH") or "admin/").strip().strip('"').strip("'")
if not admin_path:
    admin_path = "admin/"


urlpatterns = [
    path(admin_path, admin.site.urls),
    path("", include(("apps.home.urls", "home"), namespace="home")),
    path("accounts/", include(("apps.accounts.urls", "accounts"), namespace="accounts")),
    path("api/auth/", include(("apps.accounts.api.urls", "api_auth"), namespace="api_auth")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler400 = "core.views.bad_request"
handler403 = "core.views.permission_denied"
handler404 = "core.views.page_not_found"
handler405 = "core.views.method_not_allowed"
handler500 = "core.views.server_error"
