from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('dashboard/', admin.site.urls),
    path('api/', include('api.urls'))
]
