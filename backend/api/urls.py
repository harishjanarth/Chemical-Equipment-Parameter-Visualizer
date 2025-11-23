from django.urls import path
from .views import RegisterView, LoginView, UploadCSVView, SummaryView, HistoryView, GeneratePDFView, DatasetDataView
from rest_framework.permissions import AllowAny

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('upload/', UploadCSVView.as_view(), name='upload_csv'),
    path('summary/', SummaryView.as_view(), name='summary'),
    path('history/', HistoryView.as_view(), name='history'),
    path('generate_pdf/<int:dataset_id>/', GeneratePDFView.as_view(), name='generate_pdf'),
    path("dataset/<int:dataset_id>/data/", DatasetDataView.as_view()),

]
