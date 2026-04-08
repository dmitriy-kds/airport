from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from airport.models import Flight
from booking.models import Order, Ticket
from user.models import User


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Order
        fields = ("id", "created_at", "user")


class TicketSerializer(serializers.ModelSerializer):
    flight = serializers.PrimaryKeyRelatedField(queryset=Flight.objects.all())
    order = OrderSerializer(read_only=True)
    user = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight", "order", "user")
        validators = [
            UniqueTogetherValidator(
                queryset=Ticket.objects.all(),
                fields=("row", "seat", "flight"),
                message="This flight ticket already exists."
            )
        ]

    def get_user(self, obj: Ticket) -> int:
        return obj.order.user.id

    def validate(self, data: dict) -> dict:
        airplane = data["flight"].airplane
        if not 1 <= data["row"] <= airplane.rows:
            raise serializers.ValidationError(
                f"The row must be between 1 and {airplane.rows}"
            )
        if not 1 <= data["seat"] <= airplane.seats_in_row:
            raise serializers.ValidationError(
                f"The seat must be between 1 and {airplane.seats_in_row}"
            )
        return data
