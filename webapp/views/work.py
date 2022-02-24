from django.shortcuts import render
from rest_framework.response import Response
from tools.savers.seoul_saver import SeoulSaver
from webapp.models.work import Work
from rest_framework.views import APIView
from webapp.serializers import *
from django.http import HttpResponse, JsonResponse
from drf_yasg.utils import swagger_auto_schema

# 
class CreateSeoulWorkAPI(APIView):
    @swagger_auto_schema(request_body=SeoulWorkCreateSerializer)
    def post(self, request):
        data = request.data
        sale_no = data["sale_no"]
        seoul_saver = SeoulSaver(sale_no)
        workList = seoul_saver.make_work_model()
        Work.objects.bulk_create(workList)
        return JsonResponse(
            {"id":sale_no}, status=200, safe=False
        )