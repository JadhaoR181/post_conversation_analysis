# analysis/analysis_engine.py

import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from .models import ConversationAnalysis, Message

# initialize sentiment analyzer once
analyzer = SentimentIntensityAnalyzer()

# empathy and fallback keywords
EMPATHY_KEYWORDS = ["sorry", "apologize", "understand", "i'm sorry", "that must be", "i see", "i understand"]
FALLBACK_PATTERNS = [
    r"don't know", r"do not know", r"can't help", r"cannot help",
    r"i'm not sure", r"unable to", r"i don'?t have", r"no idea"
]


def analyze_conversation(conversation):
    """
    Analyzes a Conversation object and saves results into ConversationAnalysis.
    Uses simple heuristics for clarity, relevance, empathy, and sentiment.
    """

    messages = list(conversation.messages.order_by("id"))
    ai_msgs = [m for m in messages if m.sender.lower() == "ai"]
    user_msgs = [m for m in messages if m.sender.lower() == "user"]

    # ---------------- SENTIMENT ANALYSIS (user messages) ----------------
    user_text = " ".join([m.text for m in user_msgs]) if user_msgs else ""
    if user_text.strip():
        scores = analyzer.polarity_scores(user_text)
        compound = scores["compound"]
        if compound >= 0.05:
            sentiment = "positive"
        elif compound <= -0.05:
            sentiment = "negative"
        else:
            sentiment = "neutral"
    else:
        compound = 0.0
        sentiment = "neutral"

    # ---------------- CLARITY SCORE (AI sentence length heuristic) ----------------
    ai_text = " ".join([m.text for m in ai_msgs]) if ai_msgs else ""
    sentences = re.split(r'[.!?]+', ai_text)
    sent_lens = [len(s.split()) for s in sentences if s.strip()]
    avg_len = sum(sent_lens) / len(sent_lens) if sent_lens else 0

    # shorter AI messages => higher clarity (empirically)
    clarity_score = max(0.0, min(1.0, (15 - avg_len) / 15)) if avg_len else 0.5

    # ---------------- RELEVANCE SCORE (keyword overlap) ----------------
    def tokenize(text):
        return set(re.findall(r"\w+", text.lower()))

    user_tokens = set().union(*[tokenize(m.text) for m in user_msgs]) if user_msgs else set()
    ai_tokens = set().union(*[tokenize(m.text) for m in ai_msgs]) if ai_msgs else set()

    if user_tokens:
        overlap = len(user_tokens & ai_tokens)
        relevance_score = min(1.0, overlap / (len(user_tokens) + 1e-6))
    else:
        relevance_score = 0.5

    # ---------------- ACCURACY HEURISTIC ----------------
    uncertain_words = ["maybe", "might", "i think", "not sure", "possibly", "probably"]
    confident_words = ["confirmed", "definitely", "checked", "verified", "certainly"]

    if ai_msgs:
        total_ai = len(ai_msgs)
        uncertain_hits = sum(
            any(uw in m.text.lower() for uw in uncertain_words)
            for m in ai_msgs
        )
        confident_hits = sum(
            any(cw in m.text.lower() for cw in confident_words)
            for m in ai_msgs
        )
        # simple ratio: more confident words, fewer uncertainties = higher accuracy
        accuracy_score = max(0.0, min(1.0, (confident_hits + 1) / (uncertain_hits + 2)))
        if accuracy_score > 1:
            accuracy_score = 1.0
    else:
        accuracy_score = 0.5


    # ---------------- COMPLETENESS HEURISTIC ----------------
    closure_keywords_user = ["thanks", "thank you", "okay", "great", "good", "perfect"]
    closure_keywords_ai = ["resolved", "glad", "happy", "done", "fixed", "completed"]

    completeness_score = 0.0
    if user_msgs and ai_msgs:
        last_user = user_msgs[-1].text.lower()
        last_ai = ai_msgs[-1].text.lower()
        user_closure = any(k in last_user for k in closure_keywords_user)
        ai_closure = any(k in last_ai for k in closure_keywords_ai)

        if user_closure and ai_closure:
            completeness_score = 1.0
        elif ai_closure or user_closure:
            completeness_score = 0.7
        else:
            completeness_score = 0.3


    # ---------------- EMPATHY SCORE ----------------
    empathy_hits = sum(
        any(kw in m.text.lower() for kw in EMPATHY_KEYWORDS)
        for m in ai_msgs
    )
    empathy_score = empathy_hits / len(ai_msgs) if ai_msgs else 0.0

    # ---------------- FALLBACK COUNT ----------------
    fallback_count = sum(
        any(re.search(pat, m.text.lower()) for pat in FALLBACK_PATTERNS)
        for m in ai_msgs
    )

    # ---------------- RESOLUTION DETECTION ----------------
    resolved = False
    if ai_msgs:
        last_ai = ai_msgs[-1].text.lower()
        if any(word in last_ai for word in ["resolved", "fixed", "shipped", "completed", "delivered", "done"]):
            resolved = True

    # ---------------- ESCALATION LOGIC ----------------
    escalation_needed = (fallback_count >= 2) or (sentiment == "negative")

    # ---------------- RESPONSE TIME AVG (optional) ----------------
    # If timestamps exist, compute difference between messages
    diffs = []
    for i in range(1, len(messages)):
        if messages[i].timestamp and messages[i - 1].timestamp:
            dt1 = messages[i - 1].timestamp
            dt2 = messages[i].timestamp
            try:
                diff = (dt2 - dt1).total_seconds()
                if diff >= 0:
                    diffs.append(diff)
            except Exception:
                pass
    response_time_avg = sum(diffs) / len(diffs) if diffs else 5.0  # default mock value

    # ---------------- OVERALL SCORE (weighted average) ----------------
    # sentiment compound (-1 to 1) -> 0 to 1
    sentiment_score = (compound + 1) / 2
    fallback_penalty = max(0.0, 1 - (fallback_count * 0.2))

    # weights for each factor
    weights = {
        "clarity": 0.25,
        "relevance": 0.25,
        "empathy": 0.15,
        "sentiment": 0.15,
        "fallback": 0.1,
        "resolution": 0.1,
    }

    overall_score = (
        clarity_score * weights["clarity"]
        + relevance_score * weights["relevance"]
        + empathy_score * weights["empathy"]
        + sentiment_score * weights["sentiment"]
        + fallback_penalty * weights["fallback"]
        + (1.0 if resolved else 0.0) * weights["resolution"]
    )

    overall_score = round(max(0.0, min(1.0, overall_score)), 3)

    # ---------------- SAVE TO DB ----------------
    analysis, _ = ConversationAnalysis.objects.update_or_create(
        conversation=conversation,
        defaults={
            "clarity_score": round(clarity_score, 3),
            "relevance_score": round(relevance_score, 3),
            "accuracy_score": round(accuracy_score, 3),
            "completeness_score": round(completeness_score, 3),
            "sentiment": sentiment,
            "empathy_score": round(empathy_score, 3),
            "response_time_avg": round(response_time_avg, 2),
            "fallback_count": fallback_count,
            "escalation_needed": escalation_needed,
            "resolution": resolved,
            "overall_score": overall_score,
        },
    )

    return analysis
