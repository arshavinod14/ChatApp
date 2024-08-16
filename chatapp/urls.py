from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404
from django.shortcuts import render

# Function to handle 404 errors
def custom_404_view(request, exception):
    return render(request, '404.html', status=404)

# Setting the handler
handler404 = custom_404_view

# URL patterns
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('account.urls')),
    path('chats/', include('chat.urls')),
    path("__reload__/", include("django_browser_reload.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
