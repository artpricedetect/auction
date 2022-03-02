from django.contrib import admin
from webapp.models import organization


# Register your models here.
@admin.register(organization.Organization)
class Organization(admin.ModelAdmin):
    list_display = ["id", "name"]
