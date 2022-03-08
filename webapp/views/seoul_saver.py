from django.shortcuts import render
from rest_framework.response import Response
from tools.savers.seoul_saver import SeoulSaver
from webapp.models.organization import Organization
from webapp.models.sale_details import SaleDetails
from webapp.models.work import Work
from webapp.models.worksize import WorkSize
from webapp.models.lot import Lot
from rest_framework.views import APIView
from webapp.serializers.seoul_saver import *
from django.http import HttpResponse, JsonResponse
from drf_yasg.utils import swagger_auto_schema

#
class CreateSeoulAPI(APIView):
    @swagger_auto_schema(request_body=SeoulCreateSerializer)
    def post(self, request):
        data = request.data
        sale_no = data["sale_no"]

        # organization get or create
        Organization.objects.get_or_create(name="SeoulAuction")
        Organization.objects.get_or_create(name="KAuction")

        # seoul_saver 객체 생성 및 jsonData 얻어옴
        seoul_saver = SeoulSaver(sale_no)
        json_data = seoul_saver.get_json_data()
        # sale model 저장
        sale = seoul_saver.make_sale_model(json_data)
        sale.save()
        # sale details model 저장
        saleDetails = seoul_saver.make_sale_details_model(json_data, sale)
        saleDetails.save()
        # lot model 저장
        lot_list = seoul_saver.make_lot_model(json_data, sale)
        Lot.objects.bulk_create(lot_list)
        # work model 저장
        work_list, work_created_lest = seoul_saver.make_work_model(json_data)
        # make_work_model에서 이미 Work를 create하기 때문에 Work.objects.bulk_create(work_list)가 없다
        # work size model 저장
        work_size_list = seoul_saver.make_worksize_model(json_data, work_list, work_created_lest)
        WorkSize.objects.bulk_create(work_size_list)

        return JsonResponse({"id": sale_no}, status=200, safe=False)


# class CreateSeoulLotAPI(APIView):
#     @swagger_auto_schema(request_body=SeoulLotCreateSerializer)
#     def post(self, request):
#         data = request.data
#         sale_no = data["sale_no"]
#         seoul_saver = SeoulSaver(sale_no)
#         lotList = seoul_saver.make_lot_model()
#         Work.objects.bulk_create(lotList)
#         return JsonResponse(
#             {"id":sale_no}, status=200, safe=False
#         )
