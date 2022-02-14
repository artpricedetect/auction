from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("organizations/", views.ReadOrganizationAPI.as_view(), name="Read-Organization"),
    path("organizations/create", views.CreateOrganizationAPI.as_view(), name="Create-Organization"),
]
