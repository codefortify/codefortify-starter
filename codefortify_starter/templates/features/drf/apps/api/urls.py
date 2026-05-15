from django.urls import path

from apps.api.views import HealthAPIView


app_name = "api"

urlpatterns = [
    path("health/", HealthAPIView.as_view(), name="health"),
]

