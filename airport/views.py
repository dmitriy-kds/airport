from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response

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
    FlightSerializer,
    RouteListSerializer,
    RouteDetailSerializer
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
    queryset = Route.objects.all().select_related("source", "destination")
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly]

    def get_queryset(self):
        if self.action in ("list", "create"):
            queryset = Route.objects.all().select_related("source", "destination").only(
                "source__name", "destination__name"
            )
        else:
            queryset = Route.objects.all().select_related("source", "destination")
        return queryset

    def get_serializer_class(self):
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
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly]


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly]
