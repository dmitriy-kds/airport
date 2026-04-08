from django.urls import path, include
from rest_framework import routers

from booking.views import TicketViewSet, OrderViewSet

router = routers.DefaultRouter()
router.register("tickets", TicketViewSet)
router.register("orders", OrderViewSet)

app_name = "booking"

urlpatterns = [path("", include(router.urls))]
