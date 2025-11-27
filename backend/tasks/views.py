from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import date

from .models import Task
from .serializers import TaskSerializer, TaskAnalysisSerializer
from .scoring import ScoringService

class AnalyzeTasksView(APIView):

    def post(self, request):

        serializer = TaskAnalysisSerializer(data=request.data, many=True)
        
        if serializer.is_valid():
            tasks_data = serializer.validated_data
            
            try:
                analyzed_tasks = ScoringService.analyze_tasks(tasks_data)
                
                return Response(analyzed_tasks, status=status.HTTP_200_OK)
            except Exception as e:
                return Response(
                    {"error": f"Algorithm failure: {str(e)}"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SuggestTasksView(APIView):

    def get(self, request):
        tasks = Task.objects.filter(is_completed=False)
        
        serializer = TaskSerializer(tasks, many=True)
        tasks_data = serializer.data
        
        analyzed_tasks = ScoringService.analyze_tasks(tasks_data)
        
        top_3 = analyzed_tasks[:3]
        
        return Response(top_3, status=status.HTTP_200_OK)