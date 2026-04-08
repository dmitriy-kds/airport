from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from airport.models import (
    Country,
    City,
    Airport,
    Route,
    Crew,
    AirplaneType,
    Airplane,
    Flight,
)


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ("id", "name", "code")


class CitySerializer(serializers.ModelSerializer):
    country = serializers.SlugRelatedField(
        queryset=Country.objects.all(),
        slug_field="name"
    )

    class Meta:
        model = City
        fields = ("id", "name", "country")
        validators = [
            UniqueTogetherValidator(
                queryset=City.objects.all(),
                fields=["name", "country"],
                message="This city already exists in this country"
            )
        ]


class AirportSerializer(serializers.ModelSerializer):
    city = serializers.SlugRelatedField(
        queryset=City.objects.all(),
        slug_field="name"
    )

    class Meta:
        model = Airport
        fields = ("id", "name", "city", "latitude", "longitude")
        validators = [
            UniqueTogetherValidator(
                queryset=Airport.objects.all(),
                fields=["latitude", "longitude"],
                message="Airport with these coordinates already exists"
            )
        ]

    def validate_latitude(self, value: float) -> float:
        if not -90 <= value <= 90:
            raise serializers.ValidationError(
                "Latitude must be between -90 and 90."
            )
        return value

    def validate_longitude(self, value: float) -> float:
        if not -180 <= value <= 180:
            raise serializers.ValidationError(
                "Longitude must be between -180 and 180."
            )
        return value


class RouteListSerializer(serializers.ModelSerializer):
    source = serializers.SlugRelatedField(
        queryset=Airport.objects.all(),
        slug_field="name"
    )
    destination = serializers.SlugRelatedField(
        queryset=Airport.objects.all(),
        slug_field="name"
    )
    distance = serializers.FloatField(read_only=True)

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")

    def validate(self, attrs: dict) -> dict:
        if attrs["source"] == attrs["destination"]:
            raise serializers.ValidationError(
                "Route must be between different airports."
            )
        return attrs


class RouteDetailSerializer(serializers.ModelSerializer):
    source = AirportSerializer()
    destination = AirportSerializer()
    distance = serializers.FloatField(read_only=True)

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name", "image")

    def update(self, instance, validated_data):
        if "image" in validated_data and instance.image:
            instance.image.delete(save=False)
        return super().update(instance, validated_data)


class AirplaneSerializer(serializers.ModelSerializer):
    capacity = serializers.IntegerField(read_only=True)

    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "rows",
            "seats_in_row",
            "airplane_type",
            "capacity"
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Airplane.objects.all(),
                fields=["name", "airplane_type"],
                message="Airplane with this name and type already exists"
            )
        ]

    def validate_rows(self, value: int) -> int:
        if value <= 0:
            raise serializers.ValidationError(
                "Number of rows must be positive."
            )
        return value

    def validate_seats_in_row(self, value: int) -> int:
        if value <= 0:
            raise serializers.ValidationError(
                "Number of seats in row must be positive."
            )
        return value


class FlightSerializer(serializers.ModelSerializer):
    crew = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Crew.objects.all(),
    )

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "crew"
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Flight.objects.all(),
                fields=["airplane", "departure_time"],
                message="This airplane is already departing at this time."
            )
        ]

    def validate(self, attrs: dict) -> dict:
        if attrs["departure_time"] >= attrs["arrival_time"]:
            raise serializers.ValidationError(
                "Departure time must be earlier than arrival time."
            )
        return attrs

    def create(self, validated_data: dict) -> Flight:
        crew = validated_data.pop("crew", [])
        flight = Flight.objects.create(**validated_data)
        flight.crew.set(crew)
        return flight

    def update(self, instance: Flight, validated_data: dict) -> Flight:
        crew = validated_data.pop("crew", None)
        flight = super().update(instance, validated_data)
        if crew is not None:
            flight.crew.set(crew)
        return flight
