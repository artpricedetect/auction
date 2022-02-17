from django.db import models


class Picture(models.Model):
    models.AutoField(primary_key=True)  # 회화 id (유화, 조각, 수채화, 와인)
    picture_name = models.CharField(max_length=255, unique=True)
