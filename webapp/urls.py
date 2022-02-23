from django.urls import path

from webapp.views import views
from webapp.views import work

urlpatterns = [
    path("organizations/", views.ReadOrganizationAPI.as_view(), name="Read-Organization"),
    path(
        "organizations/create",
        views.CreateOrganizationAPI.as_view(),
        name="Create-Organization",
    ),
    path(
        "work/create/seoul",
        work.CreateSeoulWorkAPI.as_view(),
        name="Create-Work",
    ),
]
