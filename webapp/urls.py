from django.urls import path

from webapp.views import views, seoul_saver, kauction_view

urlpatterns = [
    path("organizations/", views.ReadOrganizationAPI.as_view(), name="Read-Organization"),
    path(
        "organizations/create",
        views.CreateOrganizationAPI.as_view(),
        name="Create-Organization",
    ),
    path(
        "seoul/create",
        seoul_saver.SeoulSaverAPI.as_view(),
        name="seoul-create",
    ),
    path("kauc/create", kauction_view.KauctionAPI.as_view(), name="kauction-create"),
]
