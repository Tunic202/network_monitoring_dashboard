from django.urls import path

from . import views


app_name = "monitoring"


urlpatterns = [
    path(
        "",
        views.dashboard,
        name="dashboard",
    ),
    path(
        "devices/add/",
        views.device_create,
        name="device_create",
    ),
    path(
        "devices/<int:device_id>/",
        views.device_detail,
        name="device_detail",
    ),
    path(
        "devices/<int:device_id>/edit/",
        views.device_edit,
        name="device_edit",
    ),
]
