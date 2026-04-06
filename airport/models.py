import math
import os
import uuid

from django.db import models
from django.db.models import (
    UniqueConstraint,
    CheckConstraint,
    Q
)
from django.utils.text import slugify


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=3, unique=True)

    class Meta:
        verbose_name_plural = "countries"

    def __str__(self) -> str:
        return f"{self.name}, {self.code}"


class City(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="cities"
    )

    class Meta:
        verbose_name_plural = "cities"
        constraints = [
            UniqueConstraint(
                fields=["name", "country"],
                name="unique_cities"
            )
        ]

    def __str__(self) -> str:
        return f"{self.name}, {self.country.code}"


class Airport(models.Model):
    name = models.CharField(max_length=200)
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name="airports"
    )
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=10, decimal_places=6)

    class Meta:
        verbose_name_plural = "airports"
        constraints = [
            UniqueConstraint(
                fields=["latitude", "longitude"],
                name="unique_coordinates"
            ),
            CheckConstraint(
                condition=(Q(longitude__gte=-180) & Q(longitude__lte=180)),
                name="longitude_between_-180_and_180",
                violation_error_message=(
                    "Longitude must be between -180 and 180"
                )
            ),
            CheckConstraint(
                condition=(Q(latitude__gte=-90) & Q(latitude__lte=90)),
                name="latitude_between_-90_and_90",
                violation_error_message=(
                    "Latitude must be between -90 and 90"
                )
            )
        ]

    def __str__(self) -> str:
        return f"{self.name}, {self.city.name}, {self.city.country.code}"


class Route(models.Model):
    source = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="source_routes"
    )
    destination = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="destination_routes"
    )

    class Meta:
        verbose_name_plural = "routes"

    @property
    def distance(self) -> float:
        lat1 = float(self.source.latitude)
        lon1 = float(self.source.longitude)
        lat2 = float(self.destination.latitude)
        lon2 = float(self.destination.longitude)

        # Convert degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

        # Differences
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        # Formula
        a = (
            math.sin(dlat / 2) ** 2 +
            math.cos(lat1) * math.cos(lat2) *
            math.sin(dlon / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))

        # Radius of earth in kilometers (approx 6371)
        return 6371 * c

    def __str__(self) -> str:
        return f"{self.source} -> {self.destination}"

class Crew(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "crew_members"

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


def create_custom_path(instance: "AirplaneType", filename: str) -> str:
    _, extension = os.path.splitext(filename)
    return os.path.join(
       "uploads/images/",
       f"{slugify(instance.name)}-{uuid.uuid4()}{extension}"
    )


class AirplaneType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(null=True, upload_to=create_custom_path)

    class Meta:
        verbose_name_plural = "airplane_types"

    def __str__(self) -> str:
        return f"{self.name}"


class Airplane(models.Model):
    name = models.CharField(max_length=150)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(
        AirplaneType,
        on_delete=models.CASCADE,
        related_name="airplanes"
    )

    class Meta:
        verbose_name_plural = "airplanes"
        constraints = [
            UniqueConstraint(
                fields=["name", "airplane_type"],
                name="unique_airplanes"
            ),
            CheckConstraint(
                condition=(Q(rows__gt=0) & Q(seats_in_row__gt=0)),
                name="positive_rows_and_seats_in_row",
                violation_error_message=(
                    "Number of rows and seats in row must be positive"
                )
            )
        ]

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self) -> str:
        return f"{self.name}, {self.airplane_type.name}, {self.capacity}"


class Flight(models.Model):
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name="flights"
    )
    airplane = models.ForeignKey(
        Airplane,
        on_delete=models.CASCADE,
        related_name="flights"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew)

    class Meta:
        verbose_name_plural = "flights"
        constraints = [
            UniqueConstraint(
                fields=[
                    "airplane",
                    "departure_time",
                ],
                name="unique_flights"
            ),
            CheckConstraint(
                condition=Q(departure_time__lt=arrival_time),
                name="departure_before_arrival",
                violation_error_message=(
                    "Departure time must be earlier than arrival time"
                )
            )
        ]

    def __str__(self) -> str:
        return (
            f"{self.route}; Airplane: {self.airplane}; "
            f"Departure: {self.departure_time}; "
            f"Arrival: {self.arrival_time}"
        )
