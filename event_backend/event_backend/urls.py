from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/events/', include('event.urls')),
    path('api/auth/', include('useraccount.urls')),
    path('api/categories/', include('category.urls')),
    path('api/orders/', include('order.urls')),
    path('api/polls/', include('poll.urls')),
    path('api/qns/', include('qns.urls')),
    path('api/relationship/', include('relationship.urls')),
    path('api/profile/', include('useraccount.urls')),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
