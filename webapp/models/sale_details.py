from django.db import models
from .sale import Sale


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
