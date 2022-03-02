from django.db import models


class Organization(models.Model):
    id = models.AutoField(primary_key=True)  # 주관사 id
    name = models.CharField(max_length=255, unique=True)  # 주관사 이름
