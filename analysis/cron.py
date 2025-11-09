# analysis/cron.py
from .models import Conversation
from .analysis_engine import analyze_conversation

def run_daily_analysis():
    """
    This function runs automatically every day via django-crontab.
    It loops through all saved conversations and updates their analysis.
    """
    conversations = Conversation.objects.all()
    for conv in conversations:
        analyze_conversation(conv)
    print(f"✅ Daily analysis completed for {conversations.count()} conversations.")
