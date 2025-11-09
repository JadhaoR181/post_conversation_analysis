from django.contrib import admin
from .models import Conversation, Message, ConversationAnalysis

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created_at")
    search_fields = ("title",)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "sender", "text")
    search_fields = ("text",)
    list_filter = ("sender",)

@admin.register(ConversationAnalysis)
class ConversationAnalysisAdmin(admin.ModelAdmin):
    list_display = (
        "conversation",
        "clarity_score",
        "relevance_score",
        "sentiment",
        "empathy_score",
        "overall_score",
        "created_at",
    )
