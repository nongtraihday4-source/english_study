from django.urls import path
from .views import GrammarAnalysisView

app_name = 'grammar'

urlpatterns = [
    path('analyze/', GrammarAnalysisView.as_view(), name='analyze_grammar'),
]
