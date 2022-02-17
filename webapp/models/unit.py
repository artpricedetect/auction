from django.db import models


class Unit(models.Model):
    models.AutoField(primary_key=True)  # 단위 코드
    unit_name = models.CharField(max_length=255, unique=True)
