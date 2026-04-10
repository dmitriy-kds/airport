from django.core.exceptions import ValidationError
from django.test import TestCase

from booking.models import Order, Ticket
from core.tests.base import BaseAPITestCase
from user.models import User


class OrderModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@email.com",
            password="1qazcde3",
        )
        self.order = Order.objects.create(
            user=self.user,
            created_at="",
        )

    def test_create_order(self):
        self.assertEqual(self.order.user, self.user)

    def test_order_str(self):
        self.assertEqual(
            str(self.order),
            f"User: {self.order.user}, Created at: {self.order.created_at}"
        )


class TicketModelTests(BaseAPITestCase):
    def test_create_ticket(self):
        self.assertEqual(self.ticket.flight, self.flight)

    def test_ticket_str(self):
        self.assertEqual(
            str(self.ticket),
            f"Order: {self.ticket.order}; Flight: {self.ticket.flight}; "
            f"Row: {self.ticket.row}; Seat: {self.ticket.seat}"
        )

    def test_unique_flight_ticket_constraint(self):
        data = {
            "row": 1,
            "seat": 1,
            "flight": self.flight,
            "order": self.order,
        }
        with self.assertRaises(ValidationError):
            Ticket.objects.create(**data)

    def test_positive_row_and_seat_constraint(self):
        data = {
            "row": -1,
            "seat": 1,
            "flight": self.flight,
            "order": self.order,
        }
        with self.assertRaises(ValidationError):
            Ticket.objects.create(**data)
        data = {
            "row": 1,
            "seat": -1,
            "flight": self.flight,
            "order": self.order,
        }
        with self.assertRaises(ValidationError):
            Ticket.objects.create(**data)

    def test_row_and_seat_within_range_constraint(self):
        data = {
            "row": 51,
            "seat": 1,
            "flight": self.flight,
            "order": self.order,
        }
        with self.assertRaises(ValidationError):
            Ticket.objects.create(**data)
        data = {
            "row": 1,
            "seat": 50,
            "flight": self.flight,
            "order": self.order,
        }
        with self.assertRaises(ValidationError):
            Ticket.objects.create(**data)
