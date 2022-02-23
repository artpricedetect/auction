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
    @swagger_auto_schema()
    def post(self, request):
        seoul_saver = SeoulSaver()
        jsonData = seoul_saver.get_json_data()
        lotsData = jsonData["lots"]
        for ld in lotsData:
            title_kor = ld["TITLE_KO_TXT"]
            title_eng = ld["TITLE_EN_TXT"]
            work = Work(title_kor=title_kor, title_eng=title_eng)
            work.save()

        return JsonResponse({"title_kor": work.title_kor, "title_eng": work.title_eng})