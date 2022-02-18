from django.db import models


class Theme(models.Model):
    models.AutoField(primary_key=True)  # 인물, 풍경, 해경, 정방형
    theme_name = models.CharField(max_length=255, unique=True)
