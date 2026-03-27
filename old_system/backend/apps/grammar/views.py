from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .services import GrammarAnalysisService

class GrammarAnalysisView(APIView):
    """
    API View to analyze grammar questions using RAG (ChromaDB + Ollama).
    """
    # AllowAny for testing, change to IsAuthenticated later if needed
    authentication_classes = []
    permission_classes = [AllowAny] 

    def post(self, request):
        question = request.data.get('text') or request.data.get('question')
        
        if not question:
            return Response(
                {"error": "Vui lòng cung cấp nội dung câu hỏi ('text' hoặc 'question')."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            service = GrammarAnalysisService()
            result = service.analyze_text(question)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
