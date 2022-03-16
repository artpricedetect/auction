from django.db import models
from webapp.models import organization


class Sale(models.Model):
    id = models.AutoField(primary_key=True)  # 경매 id
    org_id = models.ForeignKey(organization.Organization, on_delete=models.PROTECT)  # 주관사 id
    internal_id = models.CharField(max_length=255, null=True)  # 주관사 내부 경매 id
    name_kor = models.CharField(max_length=255, null=True)  # 경매 한글 이름
    name_eng = models.CharField(max_length=255, null=True)  # 경매 영문 이름

    TYPE_CHOICES = (("1", "OFFLINE"), ("2", "ONLINE"), ("3", "HONG_KONG"))
    type = models.CharField(max_length=2, choices=TYPE_CHOICES)  # 경매 타입

    location_kor = models.CharField(max_length=1500, null=True)  # 경매 위치
    location_eng = models.CharField(max_length=1500, null=True)  # 경매 위치(영어)
    start_dt = models.DateTimeField(null=True)  # 경매 시작 timestamp
    end_dt = models.DateTimeField(null=True)  # 경매 종료 timestamp
    finished_dt = models.DateTimeField(null=True)  # 경매 최종 종료 timestamp
    is_livebid = models.BooleanField(null=True)  # Live Bid 여부

    CURRENCY_CHOICES = (("KRW", "KRW"), ("USD", "USD"))
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)  # 사용 통화
