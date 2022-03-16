from django.db import models
from webapp.models.sale import Sale
from webapp.models.work import Work


class Lot(models.Model):
    models.AutoField(primary_key=True)
    sale_id = models.ForeignKey(Sale, on_delete=models.PROTECT, null=True)
    work_id = models.ForeignKey(Work, on_delete=models.PROTECT, null=True)
    lot_num = models.CharField(max_length=255, null=True)
    sold_yn = models.BooleanField(null=True)
    sold_price = models.CharField(max_length=255, null=True)
    start_price = models.CharField(max_length=255, null=True)
    est_upper_price = models.CharField(max_length=255, null=True)
    est_lower_price = models.CharField(max_length=255, null=True)
    bid_cnt = models.CharField(max_length=255, null=True)
