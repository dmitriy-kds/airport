from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import (
    UniqueConstraint,
    CheckConstraint,
    Q
)

from airport.models import Flight, Airplane


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    class Meta:
        verbose_name_plural = "orders"

    def __str__(self) -> str:
        return f"User: {self.user}, Created at: {self.created_at}"


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(
        Flight,
        on_delete=models.CASCADE,
        related_name="flight_tickets"
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="order_tickets"
    )

    class Meta:
        verbose_name_plural = "tickets"
        constraints = [
            UniqueConstraint(
                fields=["row", "seat", "flight"],
                name="unique_flight_ticket",
                violation_error_message="This flight ticket already exists"
            ),
            CheckConstraint(
                condition=(Q(row__gt=0) & Q(seat__gt=0)),
                name="positive_row_and_seat",
                violation_error_message=(
                    "Row and seat must be positive"
                )
            )
        ]

    def __str__(self) -> str:
        return (
            f"Order: {self.order}; Flight: {self.flight}; "
            f"Row: {self.row}; Seat: {self.seat}"
        )

    @staticmethod
    def validate_ticket(
            row: int,
            seat: int,
            airplane: Airplane,
            error_to_raise: type[ValidationError]
    ) -> None:
        for ticket_attr_value, ticket_attr_name, airplane_attr_name in [
            (row, "row", "rows"),
            (seat, "seat", "seats_in_row"),
        ]:
            count_attrs = getattr(airplane, airplane_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name} "
                        f"Number must be in available range: "
                        f"(1, {airplane_attr_name}): "
                        f"(1, {count_attrs})"
                    }
                )

    def clean(self) -> None:
        Ticket.validate_ticket(
            self.row,
            self.seat,
            self.flight.airplane,
            ValidationError,
        )

    def save(
        self,
        *args,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ) -> None:
        self.full_clean()
        return super().save(
            *args,
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields
        )
