import os
import jwt
import pandas as pd
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db import transaction

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser

from django.http import FileResponse

from .models import Dataset
from .utils import analyze_equipment_csv, generate_pdf_report
from .serializers import DatasetSerializer


def authenticate_request(request):
  
    auth = request.headers.get("Authorization") or request.META.get("HTTP_AUTHORIZATION")
    if not auth:
        return None

    if auth.startswith("Bearer "):
        token = auth.replace("Bearer ", "")
    else:
        token = auth

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        if not user_id:
            return None
        return User.objects.get(id=user_id)

    except Exception:
        return None



# REGISTER
@method_decorator(csrf_exempt, name="dispatch")
class RegisterView(APIView):
    permission_classes = ()
    authentication_classes = ()
    parser_classes = [JSONParser, FormParser]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response({"error": "username and password required"}, status=400)

        if User.objects.filter(username=username).exists():
            return Response({"error": "User already exists"}, status=400)

        User.objects.create_user(username=username, password=password)
        return Response({"message": "Registered successfully"})


# LOGIN
@method_decorator(csrf_exempt, name="dispatch")
class LoginView(APIView):
    permission_classes = ()
    authentication_classes = ()
    parser_classes = [JSONParser, FormParser]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response({"error": "username and password required"}, status=400)

        user = authenticate(username=username, password=password)
        if not user:
            return Response({"error": "Invalid credentials"}, status=400)

        payload = { "user_id": user.id }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

        return Response({"token": token})


@method_decorator(csrf_exempt, name="dispatch")
class UploadCSVView(APIView):
    permission_classes = ()
    authentication_classes = ()
    parser_classes = [MultiPartParser, FormParser]

    @transaction.atomic
    def post(self, request):
        user = authenticate_request(request)
        if not user:
            return Response({"error": "Not authenticated"}, status=401)

        file = request.FILES.get("file")
        if not file:
            return Response({"error": "File missing"}, status=400)

        filename = file.name
        if not filename.lower().endswith(".csv"):
            return Response({"error": "Only CSV allowed"}, status=400)

        saved_path = default_storage.save(
            f"datasets/{filename}",
            ContentFile(file.read())
        )
        full_path = os.path.join(settings.MEDIA_ROOT, saved_path)

        # run analysis
        try:
            summary, df = analyze_equipment_csv(full_path)
        except Exception as e:
            default_storage.delete(saved_path)
            return Response({"error": str(e)}, status=400)

        dataset = Dataset.objects.create(
            uploader=user,
            file=saved_path,
            summary=summary
        )

       
        qs = Dataset.objects.filter(uploader=user).order_by("-uploaded_at")
        if qs.count() > 5:
            for old in qs[5:]:
                try:
                    default_storage.delete(old.file.name)
                except:
                    pass
                old.delete()

        return Response({
            "message": "Uploaded & analyzed",
            "dataset_id": dataset.id,
            "filename": filename,
            "summary": summary
        })


class SummaryView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def get(self, request):
        user = authenticate_request(request)
        if not user:
            return Response({"error": "Not authenticated"}, status=401)

        datasets = Dataset.objects.filter(uploader=user).order_by("-uploaded_at")

        if not datasets.exists():
            return Response({"error": "No datasets yet"}, status=404)

        return Response(datasets.first().summary)


class HistoryView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def get(self, request):
        user = authenticate_request(request)
        if not user:
            return Response({"error": "Not authenticated"}, status=401)

        qs = Dataset.objects.filter(uploader=user).order_by("-uploaded_at")[:5]
        data = DatasetSerializer(qs, many=True).data
        return Response(data)


class GeneratePDFView(APIView):
    permission_classes = ()
    authentication_classes = ()

    def get(self, request, dataset_id):
        user = authenticate_request(request)
        if not user:
            return Response({"error": "Not authenticated"}, status=401)

        try:
            dataset = Dataset.objects.get(id=dataset_id, uploader=user)
        except Dataset.DoesNotExist:
            return Response({"error": "Dataset not found"}, status=404)

        pdf = generate_pdf_report(dataset.summary)

        return FileResponse(
            pdf,
            filename=f"dataset_{dataset_id}_report.pdf",
            as_attachment=True
        )


class DatasetDataView(APIView):
    permission_classes = ()
    authentication_classes = ()

    def get(self, request, dataset_id):
        user = authenticate_request(request)
        if not user:
            return Response({"error": "Not authenticated"}, status=401)

        try:
            dataset = Dataset.objects.get(id=dataset_id, uploader=user)
        except Dataset.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        df = pd.read_csv(dataset.file.path)

        return Response({
            "columns": df.columns.tolist(),
            "rows": df.head(100).to_dict(orient="records")
        })
