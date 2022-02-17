import imp
from django.db import models
from work import Work
from unit import Unit


class WorkSize(models.Model):
    work_id = models.ForeignKey(
        Work, primary_key=True, on_delete=models.PROTECT, null=False
    )  # 작품 번호
    unit_id = models.ForeignKey(Unit, on_delete=models.PROTECT, null=False)  # 단위 id
    size1 = models.CharField(max_length=255, null=True)  # 크기1 (height)
    size2 = models.CharField(max_length=255, null=True)  # 크기2 (width)
    size3 = models.CharField(max_length=255, null=True)  # 크기3 (depth)
    canvas_yn = models.BooleanField(null=True)  # 캔버스 여부
    diam_yn = models.BooleanField(null=True)  # 지름 여부
    prefix = models.CharField(max_length=255, null=True)  # 접두어
    suffix = models.CharField(max_length=255, null=True)  # 접미어
    mix_code = models.CharField(max_length=255, null=True)  # 믹스 코드..? (height로 적혀있음)
    canvas_ext_yn = models.BooleanField(null=True)  # 캔버스 EXT 여부
