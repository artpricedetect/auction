from django.db import models


class Artist(models.Model):
    SEX_CHOICES = (("1", "남성"), ("2", "여성"), ("3", "알려지지 않음"))

    id = models.AutoField(primary_key=True)
    name_kor = models.CharField(max_length=255, null=True)
    name_eng = models.CharField(max_length=255, null=True)
    born_year = models.CharField(max_length=4, null=True)
    death_year = models.CharField(max_length=4, null=True)
    education = models.CharField(max_length=255, null=True)
    profile = models.CharField(max_length=255, null=True)
    display_info = models.CharField(max_length=255, null=True)
    sex = models.CharField(max_length=2, choices=SEX_CHOICES)
    nationality = models.CharField(max_length=255, null=True)
    kauc_uid = models.CharField(max_length=255, null=True)
    sauc_uid = models.CharField(max_length=255, null=True)
