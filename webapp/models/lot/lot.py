from django.db import models
from webapp.models import Sale
import django.db


class Lot(models.Model):
    id = models.AutoField(primary_key=True)
    sale_id = models.ForeignKey(Sale, on_delete=models.PROTECT, null=False)
    # work_id = models.ForeignKey(Work, on_delete=models.PROTECT, null= False)
    lot_num = models.CharField(max_length=255, null=True)
    sold_yn = models.BooleanField(max_length=255, null=True)
    sold_price = models.CharField(max_length=255, null=True)
    start_price = models.CharField(max_length=255, null=True)
    est_upper_price = models.CharField(max_length=255, null=True)
    est_lower_price = models.CharField(max_length=255, null=True)
    bid_cnt = models.CharField(max_length=255, null=True)
