from django.db.models import QuerySet
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import ModelSerializer

from booking.models import Order
from booking.serializers import (
    OrderListSerializer,
    OrderDetailSerializer,
    OrderCreateSerializer
)


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self) -> type[ModelSerializer]:
        if self.action == "list":
            serializer_class = OrderListSerializer
        elif self.action == "retrieve":
            serializer_class = OrderDetailSerializer
        else:
            serializer_class = OrderCreateSerializer
        return serializer_class

    def get_queryset(self) -> QuerySet:
        return (Order.objects.all().filter(user=self.request.user).
                prefetch_related(
                    "order_tickets",
                    "order_tickets__flight",
                    "order_tickets__flight__route"
                )
        )

    def perform_create(self, serializer: OrderCreateSerializer) -> None:
        serializer.save(user=self.request.user)
