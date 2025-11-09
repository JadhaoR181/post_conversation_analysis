from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from analysis.views import (
    ConversationUploadView,
    AnalyseConversationView,
    ReportsView,
)
from analysis.views import trigger_daily_analysis

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", lambda req: JsonResponse({"status": "OK", "message": "PCA API is running"})),

    # API endpoints
    path("api/conversations/", ConversationUploadView.as_view(), name="upload-conversation"),
    path("api/analyse/", AnalyseConversationView.as_view(), name="analyse-conversation"),
    path("api/reports/", ReportsView.as_view(), name="reports"),
    path("api/trigger-daily-analysis/", trigger_daily_analysis, name="trigger-daily-analysis"),
]
