from django.db import models

# Create your models here.
class Organization(models.Model):
    id = models.AutoField(primary_key=True)  # 주관사 id
    name = models.CharField(max_length=255)  # 주관사 이름


class CrawlerSettings(models.Model):
    id = models.AutoField(primary_key=True)
    org_id = models.ForeignKey(Organization, on_delete=models.PROTECT, null=False)
    fetch_interval = models.IntegerField(null=True)
    last_sale_id = models.CharField(max_length=255, null=True)
    login_id = models.CharField(max_length=255, null=True)
    login_pw = models.CharField(max_length=255, null=True)
    token = models.CharField(max_length=255, null=True)
    is_api = models.BooleanField()
    api_addr = models.CharField(max_length=255, null=True)
    img_path = models.CharField(max_length=255, null=True)
    saved_data_path = models.CharField(max_length=255, null=True)
    saved_img_path = models.CharField(max_length=255, null=True)


class Sale(models.Model):
    id = models.AutoField(primary_key=True)  # 경매 id
    org_id = models.ForeignKey(Organization, on_delete=models.PROTECT)  # 주관사 id
    internal_id = models.CharField(max_length=255, null=True)  # 주관사 내부 경매 id
    name_kor = models.CharField(max_length=255, null=True)  # 경매 한글 이름
    name_eng = models.CharField(max_length=255, null=True)  # 경매 영문 이름

    TYPE_CHOICES = (("1", "OFFLINE"), ("2", "ONLINE"), ("3", "HONG_KONG"))
    type = models.CharField(max_length=2, choices=TYPE_CHOICES)  # 경매 타입

    locaton_kor = models.CharField(max_length=1500, null=True)  # 경매 위치
    location_eng = models.CharField(max_length=1500, null=True)  # 경매 위치(영어)
    start_dt = models.DateTimeField(null=True)  # 경매 시작 timestamp
    end_dt = models.DateTimeField(null=True)  # 경매 종료 timestamp
    finished_dt = models.DateTimeField(null=True)  # 경매 최종 종료 timestamp
    is_livebid = models.BooleanField(null=True)  # Live Bid 여부

    CURRENCY_CHOICES = (("KRW", "KRW"), ("USD", "USD"))
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)  # 사용 통화


class SaleDetails(models.Model):
    id = models.OneToOneField(Sale, on_delete=models.CASCADE, primary_key=True)  # 경매 id
    lot_count = models.IntegerField()  # 출품 작품 수
    sold_high = models.FloatField(null=True)  # 낙찰 최고가
    sold_low = models.FloatField(null=True)  # 낙찰 최저가
    estimate_high = models.FloatField(null=True)  # 추정가 최고가
    estimate_low = models.FloatField(null=True)  # 추정가 최저가
    sold_ratio = models.FloatField(null=True)  # 출품 작품 중 낙찰 비율
    sold_under = models.FloatField(null=True)  # 추정가 하회 낙찰 비율. 출품 작품전체 중 비율(낙찰 작품 중 % 아님)
    sold_within = models.FloatField(null=True)  # 추정가 범위 내 낙찰 비율
    sold_upper = models.FloatField(null=True)  # 추정가 상회 낙찰 비율
