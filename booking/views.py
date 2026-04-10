from typing import Any

from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
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
        return Order.objects.all().filter(
            user=self.request.user
        ).prefetch_related(
            "order_tickets",
            "order_tickets__flight",
            "order_tickets__flight__route"
        )

    def perform_create(self, serializer: OrderCreateSerializer) -> None:
        serializer.save(user=self.request.user)

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)

    @extend_schema(responses=OrderDetailSerializer)
    def retrieve(
            self,
            request: Request,
            *args: Any,
            **kwargs: Any
    ) -> Response:
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        request=OrderCreateSerializer,
        responses=OrderCreateSerializer
    )
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().create(request, *args, **kwargs)
