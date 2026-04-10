from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from airport.models import (
    Country,
    City,
    Airport,
    Route,
    Crew,
    AirplaneType,
    Airplane,
    Flight
)
from booking.models import Order, Ticket


class BaseAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            email="user@email.com",
            password="1qazcde3",
        )
        cls.order = Order.objects.create(
            user=cls.user,
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
            departure_time="2024-04-15T14:30:00+02:00",
            arrival_time="2024-04-15T18:30:00+02:00",
        )
        cls.flight2 = Flight.objects.create(
            route=cls.route,
            airplane=cls.airplane,
            departure_time="2024-06-15T14:30:00+02:00",
            arrival_time="2024-07-15T18:30:00+02:00",
        )
        cls.flight.crew.add(cls.crew)
        cls.ticket = Ticket.objects.create(
            row=1,
            seat=1,
            flight=cls.flight,
            order=cls.order,
        )
