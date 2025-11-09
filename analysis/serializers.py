from rest_framework import serializers
from .models import Conversation, Message, ConversationAnalysis


# ------------------ MESSAGE SERIALIZER ------------------
class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "sender", "text", "timestamp"]


# ------------------ CONVERSATION SERIALIZER ------------------
class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ["id", "title", "created_at", "messages"]


# ------------------ CONVERSATION CREATE SERIALIZER ------------------
class ConversationCreateSerializer(serializers.Serializer):
    """
    Used for uploading a new conversation from JSON.
    Example:
    {
      "title": "sample",
      "messages": [
        {"sender": "user", "message": "Hi"},
        {"sender": "ai", "message": "Hello! How can I help?"}
      ]
    }
    """
    title = serializers.CharField(required=False, allow_blank=True)
    messages = serializers.ListField()

    def create(self, validated_data):
        title = validated_data.get("title", "")
        messages = validated_data["messages"]

        conversation = Conversation.objects.create(title=title)

        for m in messages:
            Message.objects.create(
                conversation=conversation,
                sender=m.get("sender"),
                text=m.get("message"),
                timestamp=m.get("timestamp", None)
            )

        return conversation


# ------------------ ANALYSIS SERIALIZER ------------------
class ConversationAnalysisSerializer(serializers.ModelSerializer):
    conversation = ConversationSerializer()

    class Meta:
        model = ConversationAnalysis
        fields = "__all__"
