from django.contrib import admin
from django.urls import path
from django.http import JsonResponse

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", lambda req: JsonResponse({"status": "OK", "app": "pca_project"})),
]
