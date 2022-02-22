from django.urls import path

from webapp.views import views

urlpatterns = [
    path("organizations/", views.ReadOrganizationAPI.as_view(), name="Read-Organization"),
    path(
        "organizations/create",
        views.CreateOrganizationAPI.as_view(),
        name="Create-Organization",
    ),
    path(
        "work/create",
        views.CreateWorkAPI.as_view(),
        name="Create-Work",
    ),
]
