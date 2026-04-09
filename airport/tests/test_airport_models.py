import os
import uuid
from unittest.mock import patch
from django.utils.text import slugify

from django.db import IntegrityError
from django.test import TestCase

from airport.models import (
    Flight,
    Country,
    City,
    Airport,
    Crew,
    AirplaneType,
    Airplane,
    create_custom_path
)
from core.tests.base import BaseAPITestCase


class CountryModelTests(TestCase):
    def setUp(self):
        self.country = Country.objects.create(
            name="United Kingdom",
            code="UK"
        )

    def test_create_country(self):
        self.assertEqual(self.country.code, "UK")

    def test_country_str(self):
        self.assertEqual(
            str(self.country),
            f"{self.country.name}, {self.country.code}"
        )


class CityModelTests(TestCase):
    def setUp(self):
        self.country = Country.objects.create(
            name="United Kingdom",
            code="UK"
        )
        self.city = City.objects.create(
            name="London",
            country=self.country,
        )

    def test_create_city(self):
        self.assertEqual(self.city.country, self.country)

    def test_city_str(self):
        self.assertEqual(
            str(self.city),
            f"{self.city.name}, {self.city.country.code}"
        )

    def test_unique_cities_constraint(self):
        data = {
            "name":self.city.name,
            "country":self.city.country,
        }
        with self.assertRaises(IntegrityError):
            City.objects.create(**data)


class AirportModelTests(TestCase):
    def setUp(self):
        self.country = Country.objects.create(
            name="United Kingdom",
            code="UK"
        )
        self.city = City.objects.create(
            name="London",
            country=self.country,
        )
        self.airport = Airport.objects.create(
            name="Heathrow",
            city=self.city,
            latitude=51.4680,
            longitude=0.4550,
        )

    def test_create_airport(self):
        self.assertEqual(self.airport.city, self.city)

    def test_airport_str(self):
        self.assertEqual(
            str(self.airport),
            f"{self.airport.name}, {self.airport.city.name}, "
            f"{self.airport.city.country.code}"
        )

    def test_unique_coordinates_constraint(self):
        data = {
            "name":"Boryspil",
            "city":self.city,
            "latitude":51.4680,
            "longitude":0.4550,
        }
        with self.assertRaises(IntegrityError):
            Airport.objects.create(**data)

    def test_invalid_longitude_constraint(self):
        data = {
            "name":"Boryspil",
            "city":self.city,
            "latitude":80,
            "longitude":-200,
        }
        with self.assertRaises(IntegrityError):
            Airport.objects.create(**data)

    def test_invalid_latitude_constraint(self):
        data = {
            "name":"Boryspil",
            "city":self.city,
            "latitude":99,
            "longitude":-100,
        }
        with self.assertRaises(IntegrityError):
            Airport.objects.create(**data)


class RouteModelTests(BaseAPITestCase):
    def test_create_route(self):
        self.assertEqual(self.route.source, self.airport)

    def test_route_str(self):
        self.assertEqual(
            str(self.route),
            f"{self.route.source} -> {self.route.destination}"
        )

    def test_distance_calculations(self):
        self.assertEqual(round(self.route.distance, 2), 2122.60)


class CrewModelTests(TestCase):
    def setUp(self):
        self.crew = Crew.objects.create(
            first_name="John",
            last_name="Doe",
        )

    def test_create_crew(self):
        self.assertEqual(self.crew.first_name, "John")

    def test_crew_str(self):
        self.assertEqual(
            str(self.crew),
            f"{self.crew.first_name} {self.crew.last_name}"
        )


class AirplaneTypeModelTests(TestCase):
    def setUp(self):
        self.airplane_type = AirplaneType(name="Boeing 747")

    @patch(
        "uuid.uuid4",
        return_value=uuid.UUID("12345678123456781234567812345678")
    )
    def test_create_custom_path(self, mock_uuid):
        filename = "plane.png"
        path = create_custom_path(self.airplane_type, filename)

        # Check base directory
        self.assertTrue(path.startswith("uploads/images/"))

        # Check slugified name
        expected_slug = slugify(self.airplane_type.name)
        self.assertIn(expected_slug, path)

        # Check UUID
        self.assertIn("12345678-1234-5678-1234-567812345678", path)

        # Check extension
        self.assertTrue(path.endswith(".png"))

        # Check full expected path
        expected_path = os.path.join(
            "uploads/images/",
            f"{expected_slug}-12345678-1234-5678-1234-567812345678.png"
        )
        self.assertEqual(path, expected_path)

    def test_create_airplane_type(self):
        self.assertEqual(self.airplane_type.name, "Boeing 747")

    def test_airplane_type_str(self):
        self.assertEqual(
            str(self.airplane_type),
            f"{self.airplane_type.name}"
        )


class AirplaneModelTests(TestCase):
    def setUp(self):
        self.airplane_type = AirplaneType(name="Boeing 747")
        self.airplane_type.save()
        self.airplane = Airplane.objects.create(
            name="test_name",
            rows=50,
            seats_in_row=10,
            airplane_type=self.airplane_type,
        )

    def test_create_airplane(self):
        self.assertEqual(self.airplane.name, "test_name")

    def test_airplane_str(self):
        self.assertEqual(
            str(self.airplane),
            f"{self.airplane.name}, "
            f"{self.airplane.airplane_type.name}, "
            f"{self.airplane.capacity}"
        )

    def test_capacity_calculations(self):
        self.assertEqual(
            self.airplane.capacity, 500
        )

    def test_unique_airplanes_constraint(self):
        data = {
            "name":"test_name",
            "rows":50,
            "seats_in_row":10,
            "airplane_type":self.airplane_type,
        }
        with self.assertRaises(IntegrityError):
            Airplane.objects.create(**data)

    def test_positive_rows_constraint(self):
        data = {
            "name":"new_plane",
            "rows":-1,
            "seats_in_row":10,
            "airplane_type":self.airplane_type,
        }
        with self.assertRaises(IntegrityError):
            Airplane.objects.create(**data)

    def test_positive_seats_constraint(self):
        data = {
            "name":"new_plane",
            "rows":10,
            "seats_in_row":-1,
            "airplane_type":self.airplane_type,
        }
        with self.assertRaises(IntegrityError):
            Airplane.objects.create(**data)


class FlightModelTests(BaseAPITestCase):
    def test_create_flight(self):
        self.assertEqual(self.flight.route, self.route)

    def test_create_flight_str(self):
        self.assertEqual(
            str(self.flight),
            f"{self.flight.route}; Airplane: {self.flight.airplane}; "
            f"Departure: {self.flight.departure_time}; "
            f"Arrival: {self.flight.arrival_time}"
        )

    def test_unique_flights_constraint(self):
        data = {
            "route":self.route,
            "airplane":self.airplane,
            "departure_time":self.flight.departure_time,
            "arrival_time":self.flight.arrival_time,
        }
        with self.assertRaises(IntegrityError):
            Flight.objects.create(**data)

    def test_departure_before_arrival_constraint(self):
        data = {
            "route":self.route,
            "airplane":self.airplane,
            "departure_time":self.flight.arrival_time,
            "arrival_time":self.flight.departure_time,
        }
        with self.assertRaises(IntegrityError):
            Flight.objects.create(**data)
