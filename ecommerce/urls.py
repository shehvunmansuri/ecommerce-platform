from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def api_root(request):
    return Response({
        'message': 'Welcome to ShopWave E-Commerce API',
        'version': '1.0.0',
        'docs': 'http://localhost:8000/api/docs/',
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api_root),
    path('api/store/', include('store.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
