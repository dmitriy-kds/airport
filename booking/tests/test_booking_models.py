from django.core.exceptions import ValidationError
from django.test import TestCase

from airport.models import (
    Flight,
    Country,
    City,
    Airport,
    Route,
    Crew,
    AirplaneType,
    Airplane
)
from booking.models import Order, Ticket
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


class TicketModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="user@email.com",
            password="1qazcde3",
        )
        cls.order = Order.objects.create(
            user=cls.user,
            created_at=""
        )
        cls.country = Country.objects.create(
            name="United Kingdom",
            code="UK"
        )
        cls.country2 = Country.objects.create(
            name="Ukraine",
            code="UA"
        )
        cls.city = City.objects.create(
            name="London",
            country=cls.country,
        )
        cls.city2 = City.objects.create(
            name="Kyiv",
            country=cls.country2,
        )
        cls.airport = Airport.objects.create(
            name="Heathrow",
            city=cls.city,
            latitude=51.4680,
            longitude=0.4550,
        )
        cls.airport2 = Airport.objects.create(
            name="Boryspil",
            city=cls.city2,
            latitude=50.345001,
            longitude=30.894699,
        )
        cls.route = Route.objects.create(
            source=cls.airport,
            destination=cls.airport2,
        )
        cls.crew = Crew.objects.create(
            first_name="Tom",
            last_name="Cruise",
        )
        cls.airplane_type = AirplaneType.objects.create(
            name="Boeing 737",
        )
        cls.airplane = Airplane.objects.create(
            name="Spirit Airlines N832AS",
            rows=30,
            seats_in_row=6,
            airplane_type=cls.airplane_type,
        )
        cls.flight = Flight.objects.create(
            route=cls.route,
            airplane=cls.airplane,
            departure_time="2024-04-15T14:30:00",
            arrival_time="2024-04-15T18:30:00",
        )
        cls.flight.crew.add(cls.crew)
        cls.ticket = Ticket.objects.create(
            row=1,
            seat=1,
            flight=cls.flight,
            order=cls.order,
        )

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
            "row":1,
            "seat":1,
            "flight":self.flight,
            "order":self.order,
        }
        with self.assertRaises(ValidationError):
            Ticket.objects.create(**data)

    def test_positive_row_and_seat_constraint(self):
        data = {
            "row":-1,
            "seat":1,
            "flight":self.flight,
            "order":self.order,
        }
        with self.assertRaises(ValidationError):
            Ticket.objects.create(**data)
        data = {
            "row":1,
            "seat":-1,
            "flight":self.flight,
            "order":self.order,
        }
        with self.assertRaises(ValidationError):
            Ticket.objects.create(**data)

    def test_row_and_seat_within_range_constraint(self):
        data = {
            "row":51,
            "seat":1,
            "flight":self.flight,
            "order":self.order,
        }
        with self.assertRaises(ValidationError):
            Ticket.objects.create(**data)
        data = {
            "row":1,
            "seat":50,
            "flight":self.flight,
            "order":self.order,
        }
        with self.assertRaises(ValidationError):
            Ticket.objects.create(**data)
