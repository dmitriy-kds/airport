from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from booking.models import Order, Ticket
from booking.serializers import OrderListSerializer, OrderDetailSerializer
from core.tests.base import BaseAPITestCase


class PublicBookingApiTests(APITestCase):
    def test_unauthenticated_order_list_returns_401(self):
        response = self.client.get(reverse("booking:order-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_order_create_returns_401(self):
        response = self.client.post(reverse("booking:order-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateBookingApiTests(BaseAPITestCase):
    def setUp(self):
        self.client.force_authenticate(self.user)

    def test_authenticated_order_list_returns_200(self):
        response = self.client.get(reverse("booking:order-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_order_list_uses_list_serializer(self):
        response = self.client.get(reverse("booking:order-list"))
        queryset = Order.objects.filter(user=self.user)
        serializer = OrderListSerializer(
            queryset,
            many=True,
        )
        self.assertEqual(response.data, serializer.data)

    def test_authenticated_order_detail_uses_detail_serializer(self):
        response = self.client.get(
            reverse(
                "booking:order-detail",
                kwargs={"pk": self.order.pk}
            )
        )
        queryset = Order.objects.get(pk=self.order.pk)
        serializer = OrderDetailSerializer(queryset)
        self.assertEqual(response.data, serializer.data)

    def test_authenticated_user_cannot_see_other_users_orders(self):
        other_user = get_user_model().objects.create_user(
            email="other_user@email.com",
            password="edkfjbn390"
        )
        self.client.force_authenticate(other_user)
        other_order = Order.objects.create(user=other_user)
        Ticket.objects.create(
            row=2,
            seat=2,
            flight=self.flight2,
            order=other_order,
        ),
        response = self.client.get(reverse("booking:order-list"))
        self.assertNotEqual(self.user.email, response.data[0]["user"])
        self.assertEqual(other_user.email, response.data[0]["user"])

    def test_authenticated_create_order_same_ticket_validation(self):
        response = self.client.post(
            reverse("booking:order-list"),
            data={
                "user": self.user.email,
                "order_tickets": [
                    {
                        "row": self.ticket.row,
                        "seat": self.ticket.seat,
                        "flight": self.flight.pk,
                    }
                ],
            },
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "This flight ticket already exists.",
            response.data["order_tickets"][0]["non_field_errors"]
        )

    def test_authenticated_create_order_invalid_seat_validation(self):
        response = self.client.post(
            reverse("booking:order-list"),
            data={
                "user": self.user.email,
                "order_tickets": [
                    {
                        "row": self.ticket.row,
                        "seat": 100,
                        "flight": self.flight.pk,
                    }
                ],
            },
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            f"The seat must be between 1 and {self.airplane.seats_in_row}.",
            response.data["order_tickets"][0]["non_field_errors"]
        )

    def test_authenticated_create_order_invalid_row_validation(self):
        response = self.client.post(
            reverse("booking:order-list"),
            data={
                "user": self.user.email,
                "order_tickets": [
                    {
                        "row": 100,
                        "seat": self.ticket.seat,
                        "flight": self.flight.pk,
                    }
                ],
            },
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            f"The row must be between 1 and {self.airplane.rows}.",
            response.data["order_tickets"][0]["non_field_errors"]
        )

    def test_authenticated_create_order_user_field_is_read_only(self):
        other_user = get_user_model().objects.create_user(
            email="other_user@email.com",
            password="edkfjbn390"
        )
        response = self.client.post(
            reverse("booking:order-list"),
            data={
                "user": other_user.email,
                "order_tickets": [
                    {
                        "row": 3,
                        "seat": 3,
                        "flight": self.flight.pk,
                    }
                ],
            },
            format="json"
        )
        order = Order.objects.get(pk=response.data["id"])
        self.assertEqual(order.user, self.user)
        self.assertNotEqual(order.user, other_user)

    def test_authenticated_cannot_create_order_with_no_tickets(self):
        response = self.client.post(
            reverse("booking:order-list"),
            data={
                "user": self.user.email,
                "order_tickets": [],
            },
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Order must contain at least one ticket.",
            response.data["order_tickets"][0]
        )
