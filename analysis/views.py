import json
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Conversation, ConversationAnalysis
from .serializers import (
    ConversationCreateSerializer,
    ConversationSerializer,
    ConversationAnalysisSerializer,
)
from .analysis_engine import analyze_conversation
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from .cron import run_daily_analysis

@api_view(["GET"])
@permission_classes([AllowAny])
def trigger_daily_analysis(request):
    """
    Endpoint that triggers daily analysis manually or via external cron.
    Example: Used with cron-job.org for Windows automation.
    """
    run_daily_analysis()
    return Response({"status": "Daily analysis triggered successfully"})

# ------------------ UPLOAD CONVERSATION ENDPOINT ------------------
class ConversationUploadView(APIView):
    """
    This single endpoint accepts:
    1. Raw JSON input directly in body
    2. A .json file uploaded via multipart/form-data
    """

    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        data = None

        # Case 1: File upload
        if "file" in request.FILES:
            file_obj = request.FILES["file"]
            try:
                data = json.load(file_obj)
            except Exception as e:
                return Response({"error": f"Invalid JSON file: {e}"}, status=400)

        # Case 2: Raw JSON body
        elif request.data:
            data = request.data

        # No valid input found
        if not data:
            return Response(
                {"error": "No JSON data or file provided."}, status=400
            )

        # Validate and save conversation
        serializer = ConversationCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        conversation = serializer.save()

        return Response(
            {"conversation_id": conversation.id, "status": "Conversation stored successfully"},
            status=201,
        )


# ------------------ 2️⃣ ANALYSE CONVERSATION ------------------
class AnalyseConversationView(APIView):
    def post(self, request):
        conversation_id = request.data.get("conversation_id")

        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            return Response({"error": "Conversation not found"}, status=404)

        # Call your analyzer function (we’ll build it next)
        analysis = analyze_conversation(conversation)

        serializer = ConversationAnalysisSerializer(analysis)
        return Response(serializer.data, status=200)


# ------------------ 3️⃣ LIST ALL REPORTS ------------------
class ReportsView(APIView):
    def get(self, request):
        analyses = ConversationAnalysis.objects.all().order_by("-created_at")
        serializer = ConversationAnalysisSerializer(analyses, many=True)
        return Response(serializer.data)

