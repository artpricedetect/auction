from django.db import models
from ..models.work import Work
from ..models.unit import Unit


class WorkSize(models.Model):
    models.AutoField(primary_key=True)
    work_id = models.ForeignKey(Work, on_delete=models.PROTECT, null=False)  # 작품 번호
    size_no = models.IntegerField(null=True)  # 몇번째 size인지
    unit_id = models.CharField(max_length=255, null=True)  # 단위 id
    size1 = models.CharField(max_length=255, null=True)  # 크기1 (height)
    size2 = models.CharField(max_length=255, null=True)  # 크기2 (width)
    size3 = models.CharField(max_length=255, null=True)  # 크기3 (depth)
    canvas = models.IntegerField(null=True)  # 캔버스 여부
    diam_yn = models.CharField(max_length=255, null=True)  # 지름 여부
    prefix = models.CharField(max_length=255, null=True)  # 접두어
    suffix = models.CharField(max_length=255, null=True)  # 접미어
    mix_code = models.CharField(max_length=255, null=True)  # 믹스 코드..? (height로 적혀있음)
    canvas_ext_yn = models.BooleanField(null=True)  # 캔버스 EXT 여부
