from django.urls import path, include
from rest_framework import routers

from booking.views import OrderViewSet

router = routers.DefaultRouter()
router.register("orders", OrderViewSet, basename="order")

app_name = "booking"

urlpatterns = [path("", include(router.urls))]
