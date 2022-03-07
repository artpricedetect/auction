from django.urls import path

from webapp.views import views
from webapp.views import seoul_saver

urlpatterns = [
    path("organizations/", views.ReadOrganizationAPI.as_view(), name="Read-Organization"),
    path(
        "organizations/create",
        views.CreateOrganizationAPI.as_view(),
        name="Create-Organization",
    ),
    path(
        "create/seoul",
        seoul_saver.CreateSeoulAPI.as_view(),
        name="seoul-create",
    )
]