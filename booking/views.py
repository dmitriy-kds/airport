from django.db.models import QuerySet
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from booking.models import Order, Ticket
from booking.serializers import OrderSerializer, TicketSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet:
        return Order.objects.filter(user=self.request.user).prefetch_related("order_tickets")

    def perform_create(self, serializer: OrderSerializer) -> None:
        serializer.save(user=self.request.user)


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet:
        return Ticket.objects.filter(order__user=self.request.user).select_related("order", "flight")

    def perform_create(self, serializer: TicketSerializer) -> None:
        order = serializer.validated_data["order"]
        if order.user != self.request.user:
            raise PermissionDenied("You cannot create tickets for another user's order.")
        serializer.save()
