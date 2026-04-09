import datetime
import tempfile

from PIL import Image
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from rest_framework import status
from rest_framework.test import APITestCase

from airport.models import Flight
from airport.serializers import FlightListSerializer, FlightDetailSerializer
from core.tests.base import BaseAPITestCase


class PublicAirportApiTests(APITestCase):
    def test_unauthenticated_countries_returns_401(self):
        response = self.client.get(reverse("airport:country-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_flights_returns_401(self):
        response = self.client.get(reverse("airport:flight-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateAirportApiTests(BaseAPITestCase):
    def setUp(self):
        self.client.force_authenticate(self.user)

    def test_list_countries_returns_200(self):
        response = self.client.get(reverse("airport:country-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_flights_returns_200(self):
        response = self.client.get(reverse("airport:flight-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_flight_list_uses_list_serializer(self):
        response = self.client.get(reverse("airport:flight-list"))
        flights = Flight.objects.all()
        serializer = FlightListSerializer(
            flights,
            many=True,
            context={"request": response.wsgi_request}
        )
        self.assertEqual(response.data, serializer.data)

    def test_flight_detail_uses_detail_serializer(self):
        response = self.client.get(
            reverse("airport:flight-detail", kwargs={"pk": self.flight.pk}),
        )
        flight = Flight.objects.get(pk=self.flight.pk)
        serializer = FlightDetailSerializer(
            flight,
            context={"request": response.wsgi_request}
        )
        self.assertEqual(response.data, serializer.data)

    def test_flight_filter_by_source_returns_correct_results(self):
        data = {"source": "lo"}
        response = self.client.get(
            reverse("airport:flight-list"),
            data=data
        )
        flights = (Flight.objects.filter(
            route__source__city__name__icontains=data["source"]
        ).prefetch_related("crew").select_related("route", "airplane"))
        serializer = FlightListSerializer(
            flights,
            many=True,
            context={"request": response.wsgi_request}
        )
        self.assertEqual(response.data, serializer.data)

    def test_flight_filter_by_departure_date_returns_correct_results(self):
        data = {"departure": "2024-04-15"}
        response = self.client.get(
            reverse("airport:flight-list"),
            data=data
        )
        flights = (Flight.objects.filter(
            departure_time__date=data["departure"]
        ).prefetch_related("crew").select_related("route", "airplane"))
        serializer = FlightListSerializer(
            flights,
            many=True,
            context={"request": response.wsgi_request}
        )
        self.assertEqual(response.data, serializer.data)

    def test_non_admin_create_country_returns_403(self):
        response = self.client.post(
            reverse("airport:country-list"),
            data={"name": "Italy"}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirportApiTests(BaseAPITestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser(
            email="testadmin@test.com",
            password="dfkjbne92"
        )
        self.client.force_authenticate(self.admin)

    def test_admin_create_country_returns_201(self):
        response = self.client.post(
            reverse("airport:country-list"),
            data={
                "name": "Italy",
                "code": "IT"
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_create_flight_returns_201(self):
        response = self.client.post(
            reverse("airport:flight-list"),
            data={
                "route": self.route.pk,
                "airplane": self.airplane.pk,
                "departure_time": "2026-08-15T14:30:00",
                "arrival_time": "2026-09-16T14:30:00",
                "crew": [self.crew.pk],
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_upload_airplane_type_image_returns_200(self):
        url = reverse(
            "airport:airplanetype-upload-image",
            kwargs={"pk": self.airplane_type.pk}
        )
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)

            payload = {"image": ntf}
            response = self.client.post(url, payload, format="multipart")

        self.airplane_type.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        image_path = self.airplane_type.image.name
        self.assertTrue(image_path.startswith("uploads/images/"))
        expected_slug = slugify(self.airplane_type.name)
        self.assertIn(expected_slug, image_path)
        self.assertTrue(self.airplane_type.image.storage.exists(image_path))
        self.airplane_type.image.delete()

    def test_create_flight_invalid_times_returns_400(self):
        response = self.client.post(
            reverse("airport:flight-list"),
            data={
                "route": self.route.pk,
                "airplane": self.airplane.pk,
                "departure_time": "2026-04-15T14:30:00",
                "arrival_time": "2026-03-16T14:30:00",
                "crew": [self.crew.pk],
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_flight_duplicate_airplane_departure_returns_400(self):
        response = self.client.post(
            reverse("airport:flight-list"),
            data={
                "route": self.route.pk,
                "airplane": self.airplane.pk,
                "departure_time": self.flight.departure_time,
                "arrival_time": self.flight.arrival_time,
                "crew": [self.crew.pk],
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_flight_returns_200(self):
        update_arrival_time = timezone.make_aware(datetime.datetime(2029, 4, 15, 18, 30))
        response = self.client.patch(
            reverse(
                "airport:flight-detail",
                kwargs={"pk": self.flight.pk}
            ),
            data={
                "route": self.route.pk,
                "airplane": self.airplane.pk,
                "departure_time": self.flight.departure_time,
                "arrival_time": update_arrival_time,
                "crew": [self.crew.pk],
            }
        )
        self.flight.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.flight.arrival_time, update_arrival_time)
