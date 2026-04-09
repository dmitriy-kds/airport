from django.db.models import QuerySet
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer

from airport.models import (
    Country,
    City,
    Airport,
    Route,
    Crew,
    Airplane,
    AirplaneType,
    Flight
)
from airport.permissions import IsAdminOrIfAuthenticatedReadOnly
from airport.serializers import (
    CountrySerializer,
    CitySerializer,
    AirportSerializer,
    CrewSerializer,
    AirplaneTypeSerializer,
    AirplaneSerializer,
    RouteListSerializer,
    RouteDetailSerializer,
    FlightCreateSerializer,
    FlightListSerializer,
    FlightDetailSerializer,
    AirplaneTypeImageSerializer
)


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly]


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all().select_related("country")
    serializer_class = CitySerializer
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly]


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all().select_related("city")
    serializer_class = AirportSerializer
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly]


class RouteViewSet(viewsets.ModelViewSet):
    queryset = (Route.objects.all().
                select_related(
                    "route__source__city",
                    "route__destination__city",
                    "airplane__airplane_type"
                ).prefetch_related("crew")
    )
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly]

    def get_serializer_class(self) -> type[ModelSerializer]:
        if self.action in ("list", "create"):
            serializer_class = RouteListSerializer
        else:
            serializer_class = RouteDetailSerializer
        return serializer_class


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly]


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly]

    def get_serializer_class(self) -> type[ModelSerializer]:
        if self.action == "upload_image":
            serializer_class = AirplaneTypeImageSerializer
        else:
            serializer_class = AirplaneTypeSerializer
        return serializer_class

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser]
    )
    def upload_image(self, request: Request, pk: int = None) -> Response:
        item = self.get_object()
        serializer = self.get_serializer(item, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all().select_related("airplane_type")
    serializer_class = AirplaneSerializer
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly]


class FlightViewSet(viewsets.ModelViewSet):
    serializer_class = FlightListSerializer
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly]

    def get_serializer_class(self) -> type[ModelSerializer]:
        if self.action in ("create", "update", "partial_update"):
            serializer_class = FlightCreateSerializer
        elif self.action == "retrieve":
            serializer_class = FlightDetailSerializer
        else:
            serializer_class = FlightListSerializer
        return serializer_class

    def get_queryset(self) -> QuerySet:
        source_city = self.request.query_params.get("source")
        destination_city = self.request.query_params.get("destination")
        departure_date_str = self.request.query_params.get("departure")
        arrival_date_str = self.request.query_params.get("arrival")

        queryset = (
            Flight.objects.all().
            prefetch_related("crew").
            select_related("route", "airplane")
        )

        if source_city:
            queryset = queryset.filter(
                route__source__city__name__icontains=source_city
            )

        if destination_city:
            queryset = queryset.filter(
                route__destination__city__name__icontains=destination_city
            )

        if departure_date_str:
            field = serializers.DateField()
            try:
                valid_date = field.to_internal_value(departure_date_str)
                queryset = queryset.filter(
                    departure_time__date=valid_date
                )
            except serializers.ValidationError:
                queryset = queryset.none()

        if arrival_date_str:
            field = serializers.DateField()
            try:
                valid_date = field.to_internal_value(arrival_date_str)
                queryset = queryset.filter(
                    arrival_time__date=valid_date
                )
            except serializers.ValidationError:
                queryset = queryset.none()

        return queryset.distinct()
