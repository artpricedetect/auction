from django.shortcuts import render
from rest_framework.response import Response
from .models import sales
from rest_framework.views import APIView
from .serializers import *
from django.http import HttpResponse, JsonResponse
from drf_yasg.utils import swagger_auto_schema

# Create your views here.


def index(request):
    return HttpResponse("Hello, world. You're at the index.")


class ReadOrganizationAPI(APIView):
    @swagger_auto_schema()
    def get(self, request):
        queryset = sales.Organization.objects.all()
        serializer = OrganizationsReadSerializer(queryset, many=True)
        return JsonResponse(serializer.data, safe=False)


class CreateOrganizationAPI(APIView):
    @swagger_auto_schema(request_body=OrganizationsCreateSerializer)
    def post(self, request):
        data = request.data
        org_name = data["name"]

        organization = Organization(name=org_name)
        organization.save()
        # 웬만하면 이 안에서 돌아가는 함수들은 tools 디렉토리 내부에 만들어두기

        return JsonResponse(
            {"id": organization.id, "name": organization.name}, status=200, safe=False
        )
