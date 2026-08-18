from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/families/", include("apps.families.urls")),
    path("api/members/", include("apps.membership.urls")),
    path("api/join-requests/", include("apps.joinrequests.urls")),
    path("api/family-tree/", include("apps.familytree.urls")),
    path("api/dashboard/", include("apps.dashboard.urls")),  # Day 8 Dashboard
    path("api/posts/", include("apps.posts.urls")),        # Day 9 Posts
    path("api/comments/", include("apps.comments.urls")),    # Day 10 Comments
    path("api/", include("apps.likes.urls")),               # Day 11 Likes
    path("api-auth/", include("rest_framework.urls")),
    path("api/albums/", include("apps.albums.urls")),
     path("api/photos/", include("apps.photos.urls")),
     path("api/videos/", include("apps.videos.urls")),
     path("api/events/", include("apps.events.urls")),
     path('api/notifications/', include('apps.notifications.urls')),
    # OpenAPI Schema / Swagger UI
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
   
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)