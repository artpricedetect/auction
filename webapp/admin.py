from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(sales.Organization)
class Organization(admin.ModelAdmin):
    list_display = ["id", "name"]
