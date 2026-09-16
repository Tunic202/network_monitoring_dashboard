from django.urls import path

from . import views


app_name = "monitoring"


urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path(
        "devices/<int:device_id>/",
        views.device_detail,
        name="device_detail",
    ),
]
