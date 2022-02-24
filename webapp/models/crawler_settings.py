from django.db import models
from webapp.models import organization


class CrawlerSettings(models.Model):
    id = models.AutoField(primary_key=True)
    org_id = models.ForeignKey(organization.Organization, on_delete=models.PROTECT, null=False)
    fetch_interval = models.IntegerField(null=True)
    last_sale_id = models.CharField(max_length=255, null=True)
    login_id = models.CharField(max_length=255, null=True)
    login_pw = models.CharField(max_length=255, null=True)
    token = models.CharField(max_length=255, null=True)
    is_api = models.BooleanField()
    api_addr = models.CharField(max_length=255, null=True)
    img_path = models.CharField(max_length=255, null=True)
    saved_data_path = models.CharField(max_length=255, null=True)
    saved_img_path = models.CharField(max_length=255, null=True)
