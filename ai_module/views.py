from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .services import extract_corrections


@api_view(["POST"])
@permission_classes([IsAuthenticated])  # 🔥 THIS LINE RIGHT HERE
def process_transcript(request):
    transcript = request.data.get("transcript")

    result = extract_corrections(transcript)

    return Response(result)