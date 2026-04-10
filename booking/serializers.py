from django.db import transaction
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from airport.models import Flight
from airport.serializers import FlightDetailSerializer
from booking.models import Order, Ticket
from user.serializers import UserSerializer


class TicketSerializer(serializers.ModelSerializer):
    flight = serializers.PrimaryKeyRelatedField(
        queryset=Flight.objects.all()
    )

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight")
        validators = [
            UniqueTogetherValidator(
                queryset=Ticket.objects.all(),
                fields=("row", "seat", "flight"),
                message="This flight ticket already exists."
            )
        ]

    def validate(self, data: dict) -> dict:
        airplane = data["flight"].airplane
        if not 1 <= data["row"] <= airplane.rows:
            raise serializers.ValidationError(
                f"The row must be between 1 and {airplane.rows}."
            )
        if not 1 <= data["seat"] <= airplane.seats_in_row:
            raise serializers.ValidationError(
                f"The seat must be between 1 and {airplane.seats_in_row}."
            )
        return data


class OrderListSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field="email"
    )
    order_tickets = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ("id", "created_at", "user", "order_tickets")

    def get_order_tickets(self, instance: Order) -> list:
        return [
            (f"{ticket.flight.route}; "
             f"Seat: {ticket.seat}; "
             f"Row: {ticket.row}; "
             f"Departure: {ticket.flight.departure_time}; "
             f"Arrival: {ticket.flight.arrival_time}")
            for ticket in instance.order_tickets.all()
        ]


class OrderDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    tickets = TicketSerializer(
        many=True,
        read_only=True,
        source="order_tickets"
    )

    class Meta:
        model = Order
        fields = ("id", "created_at", "user", "tickets")


class OrderCreateSerializer(serializers.ModelSerializer):
    order_tickets = TicketSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = ("id", "order_tickets")

    def create(self, validated_data: dict) -> Order:
        with transaction.atomic():
            order_tickets = validated_data.pop("order_tickets", [])
            order = Order.objects.create(**validated_data)
            for ticket in order_tickets:
                Ticket.objects.create(order=order, **ticket)
            return order

    def validate_order_tickets(self, value: list) -> list:
        if not value:
            raise serializers.ValidationError(
                "Order must contain at least one ticket."
            )
        return value
