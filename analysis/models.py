from django.db import models


class Conversation(models.Model):
    """
    Stores a single user–AI conversation.
    """
    title = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.id} - {self.title or 'Untitled'}"


class Message(models.Model):
    """
    Individual messages belonging to a Conversation.
    sender can be 'user' or 'ai'.
    """
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.CharField(max_length=20)  # user / ai
    text = models.TextField()
    timestamp = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.sender.capitalize()}: {self.text[:40]}"


class ConversationAnalysis(models.Model):
    """
    Stores the computed analysis results of a Conversation.
    """
    conversation = models.OneToOneField(
        Conversation, on_delete=models.CASCADE, related_name="analysis"
    )

    # --- core analysis metrics ---
    clarity_score = models.FloatField(default=0.0)
    relevance_score = models.FloatField(default=0.0)
    accuracy_score = models.FloatField(null=True, blank=True)
    completeness_score = models.FloatField(null=True, blank=True)
    sentiment = models.CharField(max_length=20, default="neutral")
    empathy_score = models.FloatField(default=0.0)
    response_time_avg = models.FloatField(null=True, blank=True)  # seconds
    fallback_count = models.IntegerField(default=0)
    escalation_needed = models.BooleanField(default=False)
    resolution = models.BooleanField(default=False)
    overall_score = models.FloatField(default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analysis for Conversation {self.conversation.id}"
