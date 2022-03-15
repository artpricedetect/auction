from rest_framework.views import APIView
from django.db import transaction
from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from tools.mapping.kauc_saver import KaucSaver


class KauctionAPI(APIView):
    @swagger_auto_schema()
    @transaction.atomic()
    def post(self, request):
        kauc_saver = KaucSaver()
        kauc_saver.get_json_data()
        kauc_saver.save_sale_data()
        kauc_saver.save_artist_work_lot_data()
        kauc_saver.save_sale_details_data()

        # 추후 sale 번호에 따라 수정될 예정
        return JsonResponse({"sale_no": 146})
